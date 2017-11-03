# -*- coding: utf-8 -*-

"""
.. module:: test_ops.py

   :license: GPL / CeCILL
   :platform: Unix, Windows
   :synopsis: Executes web-service operations (ops) endpoint tests.

.. moduleauthor:: Earth System Documentation (ES-DOC) <dev@es-doc.org>

"""
import collections
import json
import os
import random
import uuid

import requests

from errata.utils import factory
from tests import utils as tu



# Set of target urls.
_URL_CREATE = "{}/1/issue/create".format(tu.BASE_URL)
_URL_SEARCH_SETUP = "{}/1/issue/search-setup".format(tu.BASE_URL)
_URL_SEARCH = "{}/1/issue/search".format(tu.BASE_URL)


def _test_search_setup():
    """ERRATA :: WS :: Postive Test :: Search setup.

    """
    # Invoke WS endpoint.
    r = requests.get(_URL_SEARCH_SETUP)

    # Assert WS response.
    tu.assert_ws_response(_URL_SEARCH_SETUP, r, fields={'project', 'severity', 'status'})


def _test_search_lite():
    import urllib

    # ... invoke WS;
    params = {
        'criteria': ','.join([
            'project:cmip6',
            'severity:medium',
            'status:new '
        ])
    }
    r = requests.get(_URL_SEARCH, params=urllib.urlencode(params))

    # Assert WS response.
    data = tu.assert_ws_response(_URL_SEARCH, r)

    print data


def test_search():
    """ERRATA :: WS :: Postive Test :: Search execution.

    """
    # Initialise criteria.
    criteria = collections.defaultdict(int)

    # Publish test issues.
    for _ in range(5):
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
