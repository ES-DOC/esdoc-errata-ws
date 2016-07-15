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
from utils import DictDiff, ListDiff


def _get_issue(obj):
    """Maps a dictionary decoded from a file to an issue instance.

    """
    print('gettin issue...')
    issue = Issue()
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
    issue.uid = obj['id']
    if 'url' in obj.keys():
        issue.url = obj['url']
    issue.workflow = obj['workflow'].lower()
    issue.datasets = obj['datasets']
    return issue


def _get_datasets(issue):
    """Yields datasets for testing purposes.

    """
    for dataset_id in issue.datasets:
        dataset = IssueDataset()
        dataset.issue_id = issue.id
        dataset.dataset_id = dataset_id
        yield dataset


def _load_issue(db_instance):
        """
        Maps an issue instance to a dictionary

        """
        print('loading issue...')
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
    print('loading datasets ')
    for dset in db_instances_list:
        print(dset)
        dset_dic = dict()
        dset_dic['issue_id'] = dset.issue_id
        dset_dic['dset_id'] = dset.dataset_id
        list_of_dic.append(dset_dic)
    return list_of_dic


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
                        except UnicodeDecodeError:
                            logger.log_db('DECODING EXCEPTION')
                        else:
                            issues.append(issue)
                            logger.log_db("issue inserted :: {}".format(issue.id))

                        # Insert related datasets.
                        for issue in issues:
                            for dataset in _get_datasets(issue):
                                try:
                                    db.session.insert(dataset)
                                except sqlalchemy.exc.IntegrityError:
                                    db.session.rollback()
                    else:
                        logger.log_db('an issue with a similar description has been already inserted to the errata db.')


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


def update(issue):
    """
    Manager's function to update the issue.
    :param issue: issue dictianary
    :return:
    """
    print('Starting update process...')
    with db.session.create():
        # Returns a single issue
        print('loading issue with id ' + str(issue['id']))
        db_issue = _load_issue(db.dao.get_issue(issue['id']))
        print(db_issue['id'])
        print('retrieving database issue...')
        # Returns a list.
        print('id = ' + str(db_issue['id']))
        print('db_issue uid is '+db_issue['uid'])
        db_dsets = _load_dsets(db.dao.get_issue_datasets_by_uid(db_issue['uid']))
        print(len(db_dsets))
        print('Got the datasets related to the issue...')
        # Workflow shouldn't revert to new if it is any other value
        if db_issue['workflow'] != WORKFLOW_NEW and issue['workflow'] == WORKFLOW_NEW:
            raise InvalidStatus
        # id, title, project, institute as well as the creation and update date should remain unchanged
        for key in NON_CHANGEABLE_KEYS:
            if str(issue[key]).lower() != str(db_issue[key]).lower():
                print('Warning: unacceptable change detected.')
                print(key, str(issue[key]), str(db_issue[key]))
                raise InvalidAttribute
        print('Done testing the non changeable keys, proceeding to check description ratio...')
    # Test the description changes by no more than 80%
        if round(SequenceMatcher(None, db_issue['description'], issue['description']).ratio(), 3)*100 < RATIO:
            logger.log_web('Description has been changed more than the allowed amount of 80%. Aborting update.')
            raise InvalidDescription
        print('ratio checks out...')
        print('applying changes...')
        keys = DictDiff(db_issue, issue)
        print(issue)
        dsets = ListDiff([k['dset_id'] for k in db_dsets], issue['datasets'])
        if (not keys.changed() and not keys.added() and not keys.removed() and not dsets.added() and
                not dsets.removed()):
            logger.log_web('Nothing to change on GitHub issue #{0}'.format(db_issue['uid']))
        else:
            for key in keys.changed():
                logger.log_web('Changing key {}'.format(key))
                logger.log_web('Old value {}'.format(db_issue[key]))
                logger.log_web('New value {}'.format(issue[key]))
                db_issue[key] = issue[key]
            for key in keys.added():
                logger.log_web('Adding key {}'.format(key))
                logger.log_web('Value {}"'.format(issue[key]))
                db_issue[key] = issue[key]
            for key in keys.removed():
                logger.log_web('REMOVE {}'.format(key))
                del db_issue[key]
            # Update issue information keeping status unchanged
            print('Done updating...')
            issue = _get_issue(db_issue)
            try:
                logger.log_db('updating issue {}'.format(issue.uid))
                db.session.update(issue)
            except UnicodeDecodeError:
                logger.log_db('DECODING EXCEPTION')
            else:
                logger.log_db('ISSUE UPDATED :: {}'.format(issue.uid))

            # processing removed datasets.
            for dset in dsets.removed():
                try:
                    # Retrieve the dataset respective to that dset_id and then delete it.
                    logger.log_db('Recreating dataset instance {}'.format(dset))
                    dataset = IssueDataset()
                    dataset.issue_id = issue.id
                    dataset.dataset_id = dset
                    logger.log_db('Deleting the formed dataset instance..')
                    db.session.delete(dataset)
                    logger.log_db('Successfully removed {}'.format(dset))
                except Exception as e:
                    logger.log_db(repr(e))

            for dset in dsets.added():
                logger.log_web('ADD {0}'.format(dset))
                dataset = IssueDataset()
                dataset.issue_id = issue.id
                dataset.dataset_id = dset
                try:
                    db.session.insert(dataset)
                except sqlalchemy.exc.IntegrityError:
                    logger.log_db('DATASET SKIPPED (already inserted) :: {}'.format(dataset.dataset_id))
                    db.session.rollback()


                # db_dsets = dsets
                # # Insert related datasets.
                # print(type(db_dsets))
                # for dataset_id in db_dsets:
                #     dataset = IssueDataset()
                #     dataset.issue_id = issue.id
                #     dataset.dataset_id = dataset_id
                #     try:
                #         db.session.insert(dataset)
                #     except sqlalchemy.exc.IntegrityError:
                #         logger.log_db('DATASET SKIPPED (already inserted) :: {}'.format(dataset.dataset_id))
                #         db.session.rollback()


