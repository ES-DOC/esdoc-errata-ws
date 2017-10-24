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
from errata.utils import constants_test



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

# Datasets identifiers keyed by institution id.
_DATASETS = collections.defaultdict(list)

# Material urls.
_MATERIALS = []


def _get_datasets(input_dir, institution_id):
    """Returns test affected  datasets.

    """
    institution_id = institution_id.upper()
    if not _DATASETS[institution_id]:
        with open("{}/datasets-01.txt".format(input_dir), 'r') as fstream:
            for l in [l.strip() for l in fstream.readlines() if l.strip()]:
                _DATASETS[institution_id].append(l.replace("IPSL", institution_id))

    return random.sample(_DATASETS[institution_id], 50)


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
        issue.project = random.choice(constants.PROJECT)['key']
        issue.date_created = _NOW - dt.timedelta(days=random.randint(30, 60))
        issue.created_by = u"test-script"
        if random.randint(0, 1):
            issue.date_closed = issue.date_created + dt.timedelta(days=4)
            issue.closed_by = "test-script"
        issue.description = u"Test issue description - {}".format(unicode(uuid.uuid4()))
        issue.institute = random.choice(constants.INSTITUTE)['key']
        issue.materials = ",".join(random.sample(constants_test.ISSUE_MATERIALS, 3))
        issue.models = random.sample(constants_test.ISSUE_MODELS, 3)
        issue.severity = random.choice(constants.SEVERITY)['key']
        issue.status = random.choice(constants.STATUS)['key']
        issue.title = u"Test issue title - {}".format(unicode(uuid.uuid4())[:50])
        issue.uid = unicode(uuid.uuid4())
        issue.updated_at = issue.date_created + dt.timedelta(days=2)
        issue.updated_by = "test-script"
        issue.variables = random.sample(constants_test.ISSUE_VARIABLES, 2)
        issue.url = u"http://errata.ipsl.upmc.fr/issue/1"

        yield issue


def _yield_issue_facets(input_dir, issue):
    """Yields issue facets for testing purposes.

    """
    def _create_facet(facet_type, facet_value):
        facet = IssueFacet()
        facet.issue_uid = issue.uid
        facet.facet_type = facet_type
        facet.facet_value = facet_value
        return facet

    experiments = set()
    models = set()

    for identifier in _get_datasets(input_dir, issue.institution_id):
        experiments.add(identifier.split(".")[4])
        models.add(identifier.split(".")[3])
        yield _create_facet(constants.FACET_TYPE_DATASET, identifier)
    for identifier in experiments:
        yield _create_facet(constants.FACET_TYPE_EXPERIMENT, identifier)
    for identifier in models:
        yield _create_facet(constants.FACET_TYPE_MODEL, identifier)
    for identifier in issue.variables:
        yield _create_facet(constants.FACET_TYPE_VARIABLE, identifier)
    yield _create_facet(constants.FACET_TYPE_MIP_ERA, issue.project)
    yield _create_facet(constants.FACET_TYPE_INSTITUTE, issue.institute)
    yield _create_facet(constants.FACET_TYPE_SEVERITY, issue.severity)
    yield _create_facet(constants.FACET_TYPE_STATUS, issue.status)


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
            except sqlalchemy.exc.IntegrityError as err:
                print err
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
