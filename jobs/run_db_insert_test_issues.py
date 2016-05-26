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
from errata.db.models import Issue, IssueDataset
from errata.utils import logger


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
    _DATASETS = []
    print 'here is the file_id ' + file_id
    if os.path.isfile("{0}/datasets-{1}.txt".format(input_dir, file_id)):
        with open("{0}/datasets-{1}.txt".format(input_dir, file_id), 'r') as fstream:
            for l in fstream.readlines():
                _DATASETS.append(l)
    return _DATASETS


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
    return issue


def get_issue_id(path_to_file):
    """
    returns the number of the issue json file.
    This will be used to identify the adequate affected dataset list.
    :param path_to_file: string containing the path to the file
    :return: the number of the dataset/issue file.
    """
    file_name = os.path.splitext(os.path.basename(path_to_file))[0]
    for s in file_name.split('-'):
        if s.isdigit():
            issue_id = s
    return issue_id


def _yield_issues(input_dir):
    """Yields issues found in json files within input directory.

    """
    for fpath in glob.iglob("{}/*.json".format(input_dir)):
        print fpath
        print get_issue_id(fpath)
        with open(fpath, 'r') as fstream:
            yield _get_issue(json.loads(fstream.read()), input_dir), get_issue_id(fpath)


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

    # with db.session.create():
    #     for issue in _yield_issues(args.input_dir):
    #         try:
    #             db.session.insert(issue)
    #         except sqlalchemy.exc.IntegrityError:
    #             logger.log_db("issue skipped (already inserted) :: {}".format(issue.uid))
    #             db.session.rollback()
    #         except UnicodeDecodeError:
    #             logger.log_db('DECODING EXCEPTION')
    #         else:
    #             logger.log_db("issue inserted :: {}".format(issue.uid))

    with db.session.create():
        issues = []
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

        for issue in issues:
            for dataset in _yield_datasets(args.input_dir, issue, issue.file_id):
                try:
                    db.session.insert(dataset)
                except sqlalchemy.exc.IntegrityError as err:
                    db.session.rollback()


# Main entry point.
if __name__ == '__main__':
    _main(_ARGS.parse_args())
