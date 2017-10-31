# -*- coding: utf-8 -*-

"""
.. module:: run_db_insert_test_issues.py
   :license: GPL/CeCIL
   :platform: Unix, Windows
   :synopsis: Inserts test issues into the errata db.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import argparse

from errata import db
from errata.utils import logger
from errata.utils import factory


# Define command line arguments.
_ARGS = argparse.ArgumentParser("Inserts test issues into errata database.")
_ARGS.add_argument(
    "-c", "--count",
    help="Numbers of issues to insert into database",
    dest="count",
    type=int
    )


def _main(args):
    """Main entry point.

    """
    with db.session.create():
        for _ in range(args.count):
            issue, facets, pid_tasks = factory.create_issue()
            db.session.insert(issue)
            for facet in facets:
                db.session.insert(facet)
            for pid_task in pid_tasks:
                db.session.insert(pid_task)
            logger.log_db("issue inserted :: {}".format(issue.uid))


# Main entry point.
if __name__ == '__main__':
    _main(_ARGS.parse_args())
