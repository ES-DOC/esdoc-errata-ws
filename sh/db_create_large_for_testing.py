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
from errata.db.models import IssueFacet
from errata.utils import logger
from errata.utils import constants


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
        issue.created_by = "test-script"
        if random.randint(0, 1):
            issue.date_closed = issue.date_created + dt.timedelta(days=4)
            issue.closed_by = "test-script"
        issue.description = u"Test issue description - {}".format(unicode(uuid.uuid4()))
        issue.institute = random.choice(constants.INSTITUTE)['key']
        issue.materials = _get_materials(input_dir)
        issue.project = random.choice(constants.PROJECT)['key']
        issue.severity = random.choice(constants.SEVERITY)['key']
        issue.status = random.choice(constants.STATUS)['key']
        issue.title = u"Test issue title - {}".format(unicode(uuid.uuid4())[:50])
        issue.uid = unicode(uuid.uuid4())
        issue.updated_at = issue.date_created + dt.timedelta(days=2)
        issue.updated_by = "test-script"
        # issue.url = "TODO"

        yield issue


def _yield_issue_facets(input_dir, issue):
    """Yields issue facets for testing purposes.

    """
    experiments = set()
    models = set()
    variables = set()
    for identifier in _get_datasets(input_dir, issue.institute):
        facet = IssueFacet()
        facet.issue_uid = issue.uid
        facet.facet_id = identifier
        facet.facet_type = constants.FACET_TYPE_DATASET
        yield facet

        experiments.add(identifier.split(".")[4])
        models.add(identifier.split(".")[3])
        # variables.add(identifier.split(".")[3])

    for identifier in experiments:
        facet = IssueFacet()
        facet.issue_uid = issue.uid
        facet.facet_id = identifier
        facet.facet_type = constants.FACET_TYPE_EXPERIMENT

        yield facet

    for identifier in models:
        facet = IssueFacet()
        facet.issue_uid = issue.uid
        facet.facet_id = identifier
        facet.facet_type = constants.FACET_TYPE_MODEL

        yield facet

    for identifier in variables:
        facet = IssueFacet()
        facet.issue_uid = issue.uid
        facet.facet_id = identifier
        facet.facet_type = constants.FACET_TYPE_VARIABLE

        yield facet


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
            for facet in _yield_issue_facets(args.input_dir, issue):
                try:
                    db.session.insert(facet)
                except sqlalchemy.exc.IntegrityError:
                    db.session.rollback()


# Main entry point.
if __name__ == '__main__':
    _main(_ARGS.parse_args())
