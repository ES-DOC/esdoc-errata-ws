# -*- coding: utf-8 -*-

"""
.. module:: run_db_insert_test_issues.py
   :license: GPL/CeCIL
   :platform: Unix, Windows
   :synopsis: Inserts test issues into the errata db.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import argparse
import json
import os
import glob

import sqlalchemy

from errata import db
from errata.db.models import Issue
from errata.db.models import IssueDataset
from errata.utils import logger
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


def _get_datasets(input_dir, file_id):
    """Returns test affected  datasets by a given issue from the respective txt file.

    """
    # Derive path to datasets list file.
    for fext in {"list", "txt"}:
        fpath = "{0}/dsets/dsets-{1}.{2}".format(input_dir, file_id, fext)
        if os.path.isfile(fpath):
            break

    # Error if not found.
    if not os.path.isfile(fpath):
        raise ValueError("Datasets list file not found: {}".format(file_id))

    # Return set of dataset identifiers.
    with open(fpath, 'r') as fstream:
        return [l.replace("\n", "") for l in fstream.readlines() if l]


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

    return issue


def _get_issue_id(fpath):
    """Returns issue json file number used to identify the adequate affected dataset list.

    """
    file_name = os.path.splitext(os.path.basename(fpath))[0]
    for fpart in file_name.split('-'):
        if fpart.isdigit():
            return fpart


def _yield_issues(input_dir):
    """Yields issues found in json files within input directory.

    """
    for fpath in glob.iglob("{}/issues/*.json".format(input_dir)):
        with open(fpath, 'r') as fstream:
            yield _get_issue(json.loads(fstream.read())), \
                  _get_issue_id(fpath)


def _yield_datasets(input_dir, issue, issue_id):
    """Yields datasets for testing purposes.

    """
    for dataset_id in _get_datasets(input_dir, issue_id):
        dataset = IssueDataset()
        dataset.issue_id = issue.id
        dataset.dataset_id = dataset_id

        yield dataset


def _main(args):
    """Main entry point.

    """
    if not os.path.exists(args.input_dir):
        raise ValueError("Input directory is invalid.")

    with db.session.create():
        issues = []
        # Insert issues found in input directory.
        for issue, issue_id in _yield_issues(args.input_dir):
            issue.file_id = issue_id
            try:
                db.session.insert(issue)
            except sqlalchemy.exc.IntegrityError:
                logger.log_db("issue skipped (already inserted) :: {}".format(issue.uid))
                db.session.rollback()
            except UnicodeDecodeError:
                logger.log_db('DECODING EXCEPTION')
            else:
                issues.append(issue)
                logger.log_db("issue inserted :: {}".format(issue.uid))

        # Insert related datasets.
        for issue in issues:
            for dataset in _yield_datasets(args.input_dir, issue, issue.file_id):
                try:
                    db.session.insert(dataset)
                except sqlalchemy.exc.IntegrityError:
                    db.session.rollback()


# Main entry point.
if __name__ == '__main__':
    _main(_ARGS.parse_args())
