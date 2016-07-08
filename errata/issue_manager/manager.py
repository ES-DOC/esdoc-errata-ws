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


def _get_issue(obj):
    """Maps a dictionary decoded from a file to an issue instance.

    """
    issue = Issue()
    issue.date_created = obj['created_at']
    if 'last_updated_at' in obj.keys():
        issue.date_updated = obj['last_updated_at']
    if 'closed_at' in obj.keys():
        issue.date_closed = obj['closed_at']
    issue.date_updated = obj['last_updated_at']
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
    issue = db.dao.get_issue(uid)
    issue.date_closed = dt.datetime.utcnow()
    # Test workflow, if Won't Fix or Resolved
    if issue.workflow in [WORKFLOW_WONT_FIX, WORKFLOW_RESOLVED]:
        issue.workflow = STATE_CLOSED
    try:
        db.dao.update(issue)
    except Exception:
        logger.log_db('an error has occurred.')
