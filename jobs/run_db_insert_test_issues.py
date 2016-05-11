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
from errata.utils import logger


# Define command line arguments.
_ARGS = argparse.ArgumentParser("Inserts test issues into errata database.")
_ARGS.add_argument(
    "-d", "--dir",
    help="Directory containing test issues in json file format",
    dest="input_dir",
    type=str
    )


def _get_issue(obj):
    """Maps a dictionary decoded from a file to an issue instance.

    """
    issue = Issue()
    issue.uid = obj['id']
    issue.title = obj['title']
    issue.description = obj['description']
    issue.date_created = obj['created_at']
    issue.date_updated = obj['last_updated_at']
    issue.date_closed = obj['closed_at']
    issue.state = obj['state']
    issue.severity = obj['severity']
    issue.url = obj['url']
    issue.materials = obj['materials']
    issue.status = 'Open' if issue.closed_date else 'Closed'

    # TODO get datasets
    issue.dsets = None

    logger.log_db('ISSUE INSTANCE HAS BEEN CREATED')

    return issue


def _yield_issues(input_dir):
    """Yields issues found in json files within input directory.

    """
    for fpath in glob.iglob("{}/*.json".format(input_dir)):
        with open(fpath, 'r') as fstream:
            yield _get_issue(json.loads(fstream.read()))


def _main(args):
    """Main entry point.

    """
    print args.input_dir
    if not os.path.exists(args.input_dir):
        raise ValueError("Input directory is invalid.")

    with db.session.create():
        for issue in _yield_issues(args.input_dir):
            try:
                logger.log_db('TRYING TO INSERT ISSUE')
                db.session.insert(issue)
            except sqlalchemy.exc.IntegrityError:
                logger.log_db("skipping issue {} :: already inserted".format(issue.uid))
                db.session.rollback()
            except UnicodeDecodeError:
                logger.log_db('DECODING EXCEPTION')


# Main entry point.
if __name__ == '__main__':
    _main(_ARGS.parse_args())
