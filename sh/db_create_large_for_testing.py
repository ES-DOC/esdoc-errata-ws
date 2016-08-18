# -*- coding: utf-8 -*-

"""
.. module:: run_db_insert_test_issues.py
   :license: GPL/CeCIL
   :platform: Unix, Windows
   :synopsis: Inserts test issues into the errata db.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import argparse
import collections
import datetime as dt
import os
import random
import uuid

import sqlalchemy

import errata
from errata import db
from errata.db.models import Issue
from errata.db.models import IssueDataset
from errata.utils import logger
from errata.utils import constants
from errata.utils.constants import STATE_CLOSED
from errata.utils.constants import STATE_OPEN


# Define command line arguments.
_ARGS = argparse.ArgumentParser("Inserts test issues into errata database.")
_ARGS.add_argument(
    "-d", "--dir",
    help="Directory containing test issues in json file format",
    dest="input_dir",
    type=str
    )
_ARGS.add_argument(
    "-c", "--count",
    help="Numbers of issues to insert into database",
    dest="count",
    type=int
    )


# Global now.
_NOW = dt.datetime.now()

# Datasets identifiers keyed by institute.
_DATASETS = collections.defaultdict(list)

# Material urls.
_MATERIALS = []


def _get_datasets(input_dir, institute):
    """Returns test affected  datasets.

    """
    institute = institute.upper()
    if not _DATASETS[institute]:
        with open("{}/datasets-01.txt".format(input_dir), 'r') as fstream:
            for l in [l.strip() for l in fstream.readlines() if l.strip()]:
                _DATASETS[institute].append(l.replace("IPSL", institute))

    return random.sample(_DATASETS[institute], 50)


def _get_materials(input_dir):
    """Returns test affected  datasets.

    """
    if not _MATERIALS:
        with open("{}/materials-01.txt".format(input_dir), 'r') as fstream:
            for l in [l.strip() for l in fstream.readlines() if l.strip()]:
                _MATERIALS.append(l)

    return ",".join(_MATERIALS)


def _yield_issue(input_dir, count):
    """Yields issue for testing purposes.

    """
    for _ in xrange(count):
        issue = Issue()
        issue.date_created = _NOW - dt.timedelta(days=random.randint(30, 60))
        issue.date_updated = issue.date_created + dt.timedelta(days=2)
        if random.randint(0, 1):
            issue.date_closed = issue.date_updated + dt.timedelta(days=2)
        issue.description = u"Test issue description - {}".format(unicode(uuid.uuid4()))
        issue.institute = random.choice(constants.INSTITUTE)['key']
        issue.materials = _get_materials(input_dir)
        issue.severity = random.choice(constants.SEVERITY)['key']
        issue.state = random.choice(constants.STATE)['key']
        issue.project = random.choice(constants.PROJECT)['key']
        issue.title = u"Test issue title - {}".format(unicode(uuid.uuid4())[:50])
        issue.uid = unicode(uuid.uuid4())
        issue.workflow = random.choice(constants.WORKFLOW)['key']

        yield issue


def _yield_datasets(input_dir, issue):
    """Yields datasets for testing purposes.

    """
    for dataset_id in _get_datasets(input_dir, issue.institute):
        dataset = IssueDataset()
        dataset.issue_uid = issue.uid
        dataset.dataset_id = dataset_id

        yield dataset


def _main(args):
    """Main entry point.

    """
    if not os.path.exists(args.input_dir):
        raise ValueError("Input directory is invalid.")

    with db.session.create():
        issues = []
        for issue in _yield_issue(args.input_dir, args.count):
            try:
                db.session.insert(issue)
            except sqlalchemy.exc.IntegrityError:
                logger.log_db("issue skipped (already inserted) :: {}".format(issue.uid))
                db.session.rollback()
            else:
                issues.append(issue)
                logger.log_db("issue inserted :: {}".format(issue.uid))

        for issue in issues:
            for dataset in _yield_datasets(args.input_dir, issue):
                try:
                    db.session.insert(dataset)
                except sqlalchemy.exc.IntegrityError as err:
                    db.session.rollback()


# Main entry point.
if __name__ == '__main__':
    _main(_ARGS.parse_args())
