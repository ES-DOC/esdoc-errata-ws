import collections
import json
import os
import random
import uuid

import pyessv
import requests

from errata_ws.utils import factory
from tests import utils as tu



# Set of target urls.
_URL_CREATE = "{}/1/issue/create".format(tu.BASE_URL)
_URL_SEARCH_SETUP = "{}/1/issue/search-setup".format(tu.BASE_URL)
_URL_SEARCH = "{}/1/issue/search".format(tu.BASE_URL)


def test_search_setup():
    """ERRATA :: WS :: SEARCH :: setup.

    """
    # Invoke WS endpoint.
    r = requests.get(_URL_SEARCH_SETUP)

    # Assert WS response.
    obj = tu.assert_ws_response(_URL_SEARCH_SETUP, r, fields={'vocabs', 'values'})

    # Assert vocabularies.
    for collection in obj['vocabs']:
        assert isinstance(pyessv.load(collection['namespace']), pyessv.Collection)
        for term in collection['terms']:
            assert isinstance(pyessv.load(term['namespace']), pyessv.Term)


def test_search():
    """ERRATA :: WS :: SEARCH :: execution.

    """
    # Initialise criteria.
    criteria = collections.defaultdict(int)

    # Publish test issues.
    for _ in range(2):
        # ... create;
        issue = factory.create_issue_dict()

        # .... publish.
        r = requests.post(
          _URL_CREATE,
          data=json.dumps(issue),
          headers={'Content-Type': 'application/json'},
          auth=tu.get_credentials()
          )
        assert r.status_code == 200

        # ... cache criteria;
        criteria[(issue['project'], issue['severity'], issue['status'])] += 1

    return

    # Perform searches:
    for project, severity, status in criteria:
        # ... invoke WS;
        params = {
            'criteria': ','.join([
                'project:{}'.format(project),
                'severity:{}'.format(severity),
                'status:{}'.format(status)
            ])
        }
        r = requests.get(_URL_SEARCH, params=params)

        # Assert WS response.
        data = tu.assert_ws_response(_URL_SEARCH, r)

        # Assert search total.
        assert data['total'] >= criteria[project, severity, status]
