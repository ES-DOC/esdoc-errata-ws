# -*- coding: utf-8 -*-

"""
.. module:: errata.issue_manager.manager.py
   :platform: Unix
   :synopsis: Manages ESGF issue onto ES-DOC

.. moduleauthor:: Guillaume Levavasseur <glipsl@ipsl.jussieu.fr>

"""

# TODO : Convert close option as update to "Resolved" workflow value
# TODO : Add delete action giving issue id, controlled by GitHub roles
# TODO : Discuss Handle Service connection/authentication only by ES-DOC from Errata Service

# Module imports
import logging as log
from errata.utils import logger
from errata import db
from errata.constants import STATE_CLOSED, STATE_OPEN, WORKFLOW_NEW, WORKFLOW_RESOLVED, WORKFLOW_WONT_FIX
from errata.db.models import Issue, IssueDataset
import sqlalchemy
from uuid import uuid4
import datetime as dt
from custom_exceptions import *
from constants import *
from difflib import SequenceMatcher


def _get_issue(obj):
    """Maps a dictionary decoded from a file to an issue instance.

    """
    issue = Issue()
    if 'date_created' in obj.keys():
        issue.date_created = obj['date_created']
    if 'date_updated' in obj.keys():
        issue.date_updated = obj['date_updated']
    if 'date_closed' in obj.keys():
        issue.date_closed = obj['date_closed']
    issue.description = obj['description']
    issue.institute = obj['institute'].lower()
    if 'materials' in obj.keys():
        issue.materials = ",".join(obj['materials'])
    issue.severity = obj['severity'].lower()
    issue.state = STATE_CLOSED if issue.date_closed else STATE_OPEN
    issue.project = obj['project'].lower()
    issue.title = obj['title']
    if 'uid' in obj.keys():
        issue.uid = obj['uid']
    if 'url' in obj.keys():
        issue.url = obj['url']
    issue.workflow = obj['workflow'].lower()
    issue.datasets = obj['datasets']
    return issue


def _get_datasets_from_issue(issue):
    """Yields datasets for testing purposes.

    """
    for dataset_id in issue.datasets:
        dataset = IssueDataset()
        dataset.issue_id = issue.id
        dataset.dataset_id = dataset_id
        yield dataset


def _get_datasets(issue, dsets):
    """Yields datasets for testing purposes.

    """
    for dataset_id in dsets:
        dataset = IssueDataset()
        dataset.issue_id = issue.id
        dataset.dataset_id = dataset_id
        yield dataset


def _load_issue(db_instance):
        """
        Maps an issue instance to a dictionary

        """
        issue = dict()
        issue['date_created'] = db_instance.date_created
        if db_instance.date_updated:
            issue['date_updated'] = db_instance.date_updated
        if db_instance.date_closed:
            issue['date_closed'] = db_instance.date_closed
        issue['description'] = db_instance.description
        issue['institute'] = db_instance.institute.upper()
        if db_instance.materials:
            issue['materials'] = [m for m in db_instance.materials.split(',')]
        issue['severity'] = db_instance.severity
        issue['project'] = db_instance.project.upper()
        issue['title'] = db_instance.title
        issue['id'] = db_instance.id
        issue['uid'] = db_instance.uid
        if db_instance.url:
            issue['url'] = db_instance.url
        issue['workflow'] = db_instance.workflow
        issue['state'] = db_instance.state
        return issue


def _load_dsets(db_instances_list):
    """
    loads a list of dataset instances into a dictionary
    :param db_instances_list: list of dataset instances
    :return: list of dictionaries
    """
    list_of_dic = []
    for dset in db_instances_list:
        dset_dic = dict()
        dset_dic['issue_id'] = dset.issue_id
        dset_dic['dset_id'] = dset.dataset_id
        list_of_dic.append(dset_dic)
    return list_of_dic


def check_status(old_issue, new_issue):
    """
    checks the status change, the new status cannot replace a status that is different than new with a new value.
    :param old_issue: old issue instance
    :param new_issue: new issue instance
    :return: Boolean
    """
    if old_issue.workflow != WORKFLOW_NEW and new_issue.workflow == WORKFLOW_NEW:
        return False
    else:
        return True


def check_ratio(old_description, new_description):
    """
    checks the change ratio in description
    :param old_description:
    :param new_description:
    :return:
    """
    change_ratio = round(SequenceMatcher(None, new_description, old_description).ratio(), 3)*100
    logger.log_web('The change between the descriptions has been detected to be about {}'.format(change_ratio))
    if change_ratio < RATIO:
        logger.log_web('Description has been changed more than the allowed amount of 80%. Aborting update.'
                       'The detected change ratio in description is around {}'.format(change_ratio))
        return False
    else:
        return True


def update_issue(old_issue, new_issue):
    """
    updates issue object instance
    :param old_issue: old instance
    :param new_issue: new instance
    :return: updated instance
    """
    for k, v in old_issue.__dict__.iteritems():
        if k in NON_CHANGEABLE_KEYS and str(old_issue.__dict__[k]).lower() != str(new_issue.__dict__[k]).lower():
            logger.log_web('Warning: unacceptable change detected.')
            logger.log_web('checking key {0}, with value {1} in db and {2} in request'.format(k,
                           str(old_issue.__dict__[k]), str(new_issue.__dict__[k])))
            raise InvalidAttribute
    if old_issue.description != new_issue.description:
        if check_ratio(old_issue.description, new_issue.description):
            old_issue.description = new_issue.description
        else:
            raise InvalidDescription
    elif old_issue.severity != new_issue.severity:
        old_issue.severity = new_issue.severity
    elif old_issue.workflow != new_issue.workflow:
        if check_status(old_issue, new_issue):
            old_issue.workflow = new_issue.workflow
        else:
            raise InvalidStatus
    elif old_issue.materials != new_issue.materials:
        old_issue.materials = new_issue.materials
    elif old_issue.state != new_issue.state:
        old_issue.state = new_issue.state
    elif old_issue.url != new_issue.url:
        old_issue.url = new_issue.url
    elif old_issue.date_updated != new_issue.date_updated:
        old_issue.date_updated = new_issue.date_updated
    elif old_issue.date_closed != new_issue.date_closed:
        old_issue.date_closed = new_issue.date_closed


def compare_dsets(old_dset, new_dset, issue):
    """
    compares the dataset lists and returns the list to be updated.
    :param old_dset: DatasetIssue Instance
    :param new_dset: list of dset id
    :param issue: Issue instance
    :return: dataset instances to be updated
    """
    # initializing return.
    dset_to_remove = []
    dset_to_add = []
    for x in old_dset:
        if x.dataset_id not in new_dset:
            logger.log_web('Appending dataset {} to removal list'.format(x.dataset_id))
            dset_to_remove.append(x)
        else:
            logger.log_web('Appending dataset {} to kept list'.format(x.dataset_id))
    # Trimming old dataset list to only ids to facilitate test.
    old_dset_id = [x.dataset_id for x in old_dset]
    for x in new_dset:
        if x not in old_dset_id:
            logger.log_web('Appending dataset {} to adding list'.format(x))
            dset_to_add.append(x)
        else:
            logger.log_web('Dataset {} was found within existing datasets, skipping.'.format(x))
    # converting to dataset object instance
    dset_to_add = _get_datasets(issue, dset_to_add)
    return dset_to_add, dset_to_remove


def create(issue):
        """
        Create an issue entry into the database.

        :param issue: json of the issue.
        :raises Error: If the issue registration fails without any result

        """
        issues = []
        # Convert dictionary into Issue instance
        log.info('STARTED INJECTING A NEW ISSUE...')
        issue = _get_issue(issue)
        log.info('JSON CONVERTED INTO ISSUE INSTANCE...')
        with db.session.create():
            # Adding attributes
            log.info('ADDING ATTRIBUTES...')
            issue.uid = str(uuid4())
            issue.workflow = WORKFLOW_NEW
            # Insert issue entry into database
            with db.session.create():
                with db.session.create():
                    # Check if description exists within db already. Duplication of description is not tolerated.
                    logger.log_db('checking issue description for duplicates.')
                    if db.dao.check_description(issue.description):
                        # Insert issues
                        logger.log_db('description checks out, proceeding to issue insertion.')
                        try:
                            db.session.insert(issue)
                        except sqlalchemy.exc.IntegrityError:
                            logger.log_db("issue skipped (already inserted) :: {}".format(issue.id))
                            db.session.rollback()
                            return "issue skipped (already inserted) :: {}".format(issue.id), -1
                        except UnicodeDecodeError:
                            logger.log_db('DECODING EXCEPTION')
                            return 'Decoding Exception', -1
                        else:
                            issues.append(issue)
                            logger.log_db("issue inserted :: {}".format(issue.id))
                            return 'successfully inserted', 0

                        # Insert related datasets.
                        for issue in issues:
                            for dataset in _get_datasets_from_issue(issue):
                                try:
                                    db.session.insert(dataset)
                                except sqlalchemy.exc.IntegrityError:
                                    db.session.rollback()
                    else:
                        logger.log_db('an issue with a similar description has been already inserted to the errata db.')
                        return 'an issue with a similar description has been already inserted to the errata db', -1


def close(uid):
    """
    Manager's function that takes care of closing issues.
    :param uid: unique identifier of issues.
    :return:
    """
    print("started close function, retrieving issue...")
    with db.session.create():
        issue = db.dao.get_issue(uid)
        # Test workflow, if Won't Fix or Resolved
        if issue.workflow in [WORKFLOW_WONT_FIX, WORKFLOW_RESOLVED]:
            issue.state = STATE_CLOSED
            issue.date_closed = dt.datetime.utcnow()
        try:
            db.session.update(issue)
        except Exception as e:
            logger.log_db('an error has occurred.')
            logger.log_db(repr(e))
            return repr(e), -1
        return 'issue closed', 0


def update(issue):
    """
    Manager's function to update the issue.
    :param issue: issue dictianary
    :return:
    """
    new_issue = _get_issue(issue)
    with db.session.create():
        # Returns a single issue
        logger.log_web('Loading issue with id  {}'.format(new_issue.uid))
        db_issue = db.dao.get_issue(new_issue.uid)
        logger.log_web('database issue retrieved')
        # Workflow shouldn't revert to new if it is any other value
        logger.log_web('Comparing instances and updating..')
        try:
            update_issue(db_issue, new_issue)
        except InvalidDescription as e:
            return e.msg, -1
        except InvalidAttribute as e:
            return e.msg, -1
        except InvalidStatus as e:
            return e.msg, -1

        # Updating affected dataset list
        dsets_to_add, dsets_to_remove = compare_dsets(db.dao.get_issue_datasets_by_uid(db_issue.uid), issue['datasets']
                                                      , db_issue)
        logger.log_web('Got the datasets related to the issue.')
        try:
            db.session.update(db_issue)
            logger.log_db('issue updated.')
            for dset in dsets_to_remove:
                db.session.delete(dset)
                logger.log_db('Removing dataset {}'.format(dset.dataset_id))
                db.session.commit()
            logger.log_db('Extra datasets were removed.')
            # for x in dsets_to_add:
            #     print(x)
            for dset in dsets_to_add:
                logger.log_db('processing dataset {}'.format(dset.dataset_id))
                db.session.insert(dset)
                logger.log_db('Adding dataset {}'.format(dset.dataset_id))
            logger.log_db('Additional datasets were added.')
            db_issue = db.dao.get_issue(db_issue.uid)

        except UnicodeDecodeError:
            logger.log_db('DECODING EXCEPTION')
        else:
            logger.log_db('ISSUE UPDATED')
        return SUCCESS_MESSAGE, 0

