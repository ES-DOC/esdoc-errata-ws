import argparse
import json
import os

import requests

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

# Web-service endpoint: create issue.
_URL_CREATE = "{}/1/issue/create".format(os.getenv("ERRATA_API"))



def _main(args):
    """Main entry point.

    """
    for _ in range(args.count):
        issue = factory.create_issue_dict()
        r = requests.post(
            _URL_CREATE,
            data=json.dumps(issue),
            headers={'Content-Type': 'application/json'},
            auth=(
                os.getenv('ERRATA_WS_TEST_LOGIN'),
                os.getenv('ERRATA_WS_TEST_TOKEN')
            )
        )
        if r.status_code == 200:
            logger.log("issue inserted :: {}".format(issue['uid']))
        else:
            logger.log_error(r.text)


# Main entry point.
if __name__ == '__main__':
    _main(_ARGS.parse_args())
