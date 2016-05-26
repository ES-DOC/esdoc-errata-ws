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
import json
import os
import glob

import sqlalchemy

from errata import db
from errata.constants import STATE_CLOSED
from errata.constants import STATE_OPEN
from errata.db.models import Issue
from errata.utils import logger


# Define command line arguments.
_ARGS = argparse.ArgumentParser("Inserts test issues into errata database.")
_ARGS.add_argument(
    "-d", "--dir",
    help="Directory containing test issues in json file format",
    dest="input_dir",
    type=str
    )

# Datasets identifiers keyed by institute.
_DATASETS = collections.defaultdict(list)


def _get_datasets(input_dir, institute):
    """Returns test affected  datasets.

    """
    institute = institute.upper()
    if not _DATASETS[institute]:
        with open("{}/datasets-01.txt".format(input_dir), 'r') as fstream:
            for l in [l.strip() for l in fstream.readlines() if l.strip()]:
                _DATASETS[institute].append(l.replace("IPSL", institute))

    return _DATASETS[institute]


def _get_issue(obj, input_dir):
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
    issue.materials = ",".join(obj['materials'])
    issue.severity = obj['severity'].lower()
    issue.state = STATE_CLOSED if issue.date_closed else STATE_OPEN
    issue.project = obj['project'].lower()
    issue.title = obj['title']
    issue.uid = obj['id']
    issue.url = obj['url']
    issue.workflow = obj['workflow'].lower()
    issue.datasets = _get_datasets(input_dir, issue.institute)

    return issue


def _yield_issues(input_dir):
    """Yields issues found in json files within input directory.

    """
    for fpath in glob.iglob("{}/*.json".format(input_dir)):
        with open(fpath, 'r') as fstream:
            yield _get_issue(json.loads(fstream.read()), input_dir)


def _main(args):
    """Main entry point.

    """
    if not os.path.exists(args.input_dir):
        raise ValueError("Input directory is invalid.")

    with db.session.create():
        for issue in _yield_issues(args.input_dir):
            try:
                db.session.insert(issue)
            except sqlalchemy.exc.IntegrityError:
                logger.log_db("issue skipped (already inserted) :: {}".format(issue.uid))
                db.session.rollback()
            except UnicodeDecodeError:
                logger.log_db('DECODING EXCEPTION')
            else:
                logger.log_db("issue inserted :: {}".format(issue.uid))


# Main entry point.
if __name__ == '__main__':
    _main(_ARGS.parse_args())
