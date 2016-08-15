# -*- coding: utf-8 -*-

"""
.. module:: errata.issue_manager.manager.py
   :platform: Unix
   :synopsis: Manages ESGF issue onto ES-DOC

.. moduleauthor:: Guillaume Levavasseur <glipsl@ipsl.jussieu.fr>

"""
import datetime as dt
import difflib

import sqlalchemy

from errata import db
from errata.utils.constants import STATE_CLOSED
from errata.utils.constants import STATE_OPEN
from errata.utils.constants import WORKFLOW_NEW
from errata.utils.constants import WORKFLOW_RESOLVED
from errata.utils.constants import WORKFLOW_WONT_FIX
from errata.db.models import Issue
from errata.db.models import IssueDataset
from errata.utils import logger

from errata.utils.exceptions import DuplicateIssueDescriptionError
from errata.utils.exceptions import ImmutableIssueAttributeError
from errata.utils.exceptions import InvalidIssueStatusError



# TODO : Convert close option as update to "Resolved" workflow value
# TODO : Add delete action giving issue id, controlled by GitHub roles
# TODO : Discuss Handle Service connection/authentication only by ES-DOC from Errata Service



def _decode_issue(obj):
    """Decodes an issue instance from a dictionary.

    """
    issue = Issue()
    issue.date_created = obj.get('date_created', issue.date_created)
    issue.date_closed = obj.get('date_closed')
    issue.date_created = obj.get('date_created')
    issue.description = obj['description']
    issue.institute = obj['institute'].lower()
    issue.materials = ",".join(obj.get('materials', []))
    issue.severity = obj['severity'].lower()
    issue.state = STATE_CLOSED if issue.date_closed else STATE_OPEN
    issue.project = obj['project'].lower()
    issue.title = obj['title']
    issue.uid = obj.get('uid', issue.uid)
    issue.uid = obj.get('id', issue.uid)
    issue.url = obj.get('url')
    issue.workflow = obj['workflow'].lower()
    issue.datasets = obj['datasets']

    return issue


def _decode_datasets(issue, dsets=None):
    """Decodes issue datasets.

    """
    dsets = dsets if dsets else issue.datasets
    for dataset_id in dsets:
        dataset = IssueDataset()
        dataset.issue_id = issue.id
        dataset.dataset_id = dataset_id

        yield dataset


def _encode_issue(issue):
    """Encodes an issue instance to a dictionary.

    """
    obj = dict()
    obj['date_created'] = issue.date_created
    obj['description'] = issue.description
    obj['id'] = issue.id
    obj['institute'] = issue.institute.upper()
    obj['project'] = issue.project.upper()
    obj['severity'] = issue.severity
    obj['state'] = issue.state
    obj['title'] = issue.title
    obj['uid'] = issue.uid
    obj['workflow'] = issue.workflow

    if issue.date_closed:
        obj['date_closed'] = issue.date_closed
    if issue.date_updated:
        obj['date_updated'] = issue.date_updated
    if issue.materials:
        obj['materials'] = [m for m in issue.materials.split(',')]
    if issue.url:
        obj['url'] = issue.url

    return obj


def _encode_datasets(datasets):
    """Encodes a list of dataset instances to a list of dictionaries.

    """
    return [{
        'dset_id': i.dataset_id,
        'issue_id': i.issue_id
    } for i in datasets]


def _check_status(old_issue, new_issue):
    """Checks the status change, the new status cannot replace a status that is different than new with a new value.

    """
    if old_issue.workflow != WORKFLOW_NEW and new_issue.workflow == WORKFLOW_NEW:
        return False

    return True


def _check_ratio(old_description, new_description):
    """Checks description change ratio.

    """
    # Determine change ratio.
    change_ratio = round(difflib.SequenceMatcher(None, new_description, old_description).ratio(), 3) * 100
    logger.log_web("Issue description change ratio = {}".format(change_ratio))

    # False if ratio exceeds limit.
    if change_ratio < RATIO:
        logger.log_web("Description has been changed more than the allowed amount of {}%. Aborting update.  The detected change ratio in description is around {}".format(100 - RATIO, change_ratio))
        return False

    return True


def _update_issue(old_issue, new_issue):
    """Updates issue object instance.

    """
    for k, _ in old_issue.__dict__.iteritems():
        if k in IMMUTABLE_KEYS and str(old_issue.__dict__[k]).lower() != str(new_issue.__dict__[k]).lower():
            logger.log_web('Old issue creation date {}'.format(old_issue.__dict__['date_created']))
            logger.log_web('New issue creation date {}'.format(new_issue.__dict__['date_created']))
            logger.log_web_warning('unacceptable change detected. Attempted to change the key {}.'.format(k))
            logger.log_web('checking key {0}, with value {1} in db and {2} in request'.format(k,
                           str(old_issue.__dict__[k]), str(new_issue.__dict__[k])))
            raise ImmutableIssueAttributeError()

    if old_issue.description != new_issue.description:
        if _check_ratio(old_issue.description, new_issue.description):
            old_issue.description = new_issue.description
        else:
            raise IssueDescriptionChangeRatioError()

    elif old_issue.severity != new_issue.severity:
        old_issue.severity = new_issue.severity

    elif old_issue.workflow != new_issue.workflow:
        if _check_status(old_issue, new_issue):
            old_issue.workflow = new_issue.workflow
        else:
            raise InvalidIssueStatusError()

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


def _compare_dsets(old_dset, new_dset, issue):
    """Compares the dataset lists and returns the list to be updated.

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
    dset_to_add = _decode_datasets(issue, dset_to_add)

    return dset_to_add, dset_to_remove


def create(issue):
        """
        Create an issue entry into the database.

        :param issue: json of the issue.
        :raises Error: If the issue registration fails without any result

        """
        # Convert dictionary into Issue instance
        logger.log('STARTED INJECTING A NEW ISSUE...')
        issue = _decode_issue(issue)
        logger.log('JSON CONVERTED INTO ISSUE INSTANCE...')

        with db.session.create():
            # Adding attributes
            logger.log('ADDING ATTRIBUTES...')
            # issue.uid = str(uuid4())
            # issue.workflow = WORKFLOW_NEW

            # Insert issue entry into database
            # Insert issues
            logger.log_db('description checks out, proceeding to issue insertion.')
            try:
                db.session.insert(issue)
            except sqlalchemy.exc.IntegrityError:
                logger.log_db("issue skipped (already inserted) :: {}".format(issue.id))
                db.session.rollback()
                return "issue skipped (already inserted) :: {}".format(issue.id), -1, None
            except UnicodeDecodeError:
                logger.log_db('DECODING EXCEPTION')
                return 'Decoding Exception', -1, None
            else:
                logger.log_db("issue inserted :: {}".format(issue.id))
                return 'successfully inserted', 0, issue.date_created

            # Insert related datasets.
            for dataset in _decode_datasets(issue):
                try:
                    db.session.insert(dataset)
                except sqlalchemy.exc.IntegrityError:
                    db.session.rollback()


def close(uid):
    """
    Manager's function that takes care of closing issues.
    :param uid: unique identifier of issues.
    :return:
    """
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
                return repr(e), -1, None

            return 'issue closed', 0, issue.date_closed
        else:
            return 'issue cant be closed for workflow conflicts', -1, None


def update(issue):
    """
    Manager's function to update the issue.
    :param issue: issue dictianary
    :return:
    """
    new_issue = _decode_issue(issue)
    with db.session.create():
        # Returns a single issue
        logger.log_web('Loading issue with id  {}'.format(new_issue.uid))
        db_issue = db.dao.get_issue(new_issue.uid)
        logger.log_web('database issue retrieved')

        # Workflow shouldn't revert to new if it is any other value
        logger.log_web('Comparing instances and updating..')
        try:
            _update_issue(db_issue, new_issue)
        except (
            IssueDescriptionChangeRatioError,
            ImmutableIssueAttributeError,
            InvalidIssueStatusError
            ) as e:
            return e.msg, -1, None

        # Updating affected dataset list
        dsets_to_add, dsets_to_remove = _compare_dsets(db.dao.get_issue_datasets_by_uid(db_issue.uid), issue['datasets'], db_issue)
        logger.log_web('Got the datasets related to the issue.')

        try:
            db.session.update(db_issue)
            logger.log_db('issue updated.')
            for dset in dsets_to_remove:
                db.session.delete(dset)
                logger.log_db('Removing dataset {}'.format(dset.dataset_id))
                db.session.commit()
            logger.log_db('Extra datasets were removed.')
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

        return "UPDATE SUCCEEDED.", 0, db_issue.date_updated

