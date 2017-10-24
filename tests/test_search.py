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

from errata.utils.constants import INSTITUTE
from errata.utils.constants import PROJECT
from errata.utils.constants import SEVERITY
from errata.utils.constants import STATUS
from errata.utils.constants_test import ISSUE

from tests import utils as tu



# Set of target urls.
_URL_CREATE = "{}/1/issue/create".format(tu.BASE_URL)
_URL_SEARCH_SETUP = "{}/1/issue/search-setup".format(tu.BASE_URL)
_URL_SEARCH = "{}/1/issue/search".format(tu.BASE_URL)


def test_search_setup():
    """ERRATA :: WS :: Postive Test :: Search setup.

    """
    # Invoke WS endpoint.
    r = requests.get(_URL_SEARCH_SETUP)

    # Assert WS response.
    tu.assert_ws_response(_URL_SEARCH_SETUP, r, fields={'institute', 'project', 'severity', 'status', 'facet'})


def test_search():
    """ERRATA :: WS :: Postive Test :: Search execution.

    """
    # Initialise criteria.
    criteria = collections.defaultdict(int)

    # Publish test issues.
    for _ in range(5):
    # for _ in range(50):
        # ... create;
        issue = ISSUE.copy()
        issue['uid'] = unicode(uuid.uuid4())
        issue['severity'] = random.choice(SEVERITY)['key']
        issue['status'] = random.choice(STATUS)['key']

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
          'project': project,
          'severity': severity,
          'status': status
        }
        r = requests.get(_URL_SEARCH, params=params)

        # Assert WS response.
        data = tu.assert_ws_response(_URL_SEARCH, r)

        # Assert search total.
        assert data['total'] >= criteria[project, severity, status]
