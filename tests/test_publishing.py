# -*- coding: utf-8 -*-

"""
.. module:: test_publishing.py

   :license: GPL / CeCILL
   :platform: Unix, Windows
   :synopsis: Executes web-service publishing endpoint tests.

.. moduleauthor:: Earth System Documentation (ES-DOC) <dev@es-doc.org>

"""
import datetime as dt
import json
import os
import random
import urllib

import requests

from errata.utils import constants
from errata.utils.constants_test import ISSUE
from errata.utils.constants_test import ISSUE_DATASETS

from tests import utils as tu



# Set of target urls.
_URL_CLOSE = '{}/1/issue/close?'.format(tu.BASE_URL)
_URL_CLOSE += urllib.urlencode({'uid': ISSUE['uid'], 'status': constants.STATUS_RESOLVED})
_URL_CREATE = "{}/1/issue/create".format(tu.BASE_URL)
_URL_RETRIEVE = '{}/1/issue/retrieve?'.format(tu.BASE_URL)
_URL_RETRIEVE += urllib.urlencode({'uid': ISSUE['uid']})
_URL_UPDATE = "{}/1/issue/update".format(tu.BASE_URL)


def test_create():
    """ERRATA :: WS :: Postive Test :: Create issue.

    """
    # Invoke WS endpoint.
    response = requests.post(
        _URL_CREATE,
        data=json.dumps(ISSUE),
        headers={'Content-Type': 'application/json'},
        auth=tu.get_credentials()
        )

    # Assert WS response.
    tu.assert_ws_response(_URL_CREATE, response)


def test_retrieve():
    """ERRATA :: WS :: Postive Test :: Retrieve issue.

    """
    # Invoke WS endpoint.
    response = requests.get(_URL_RETRIEVE)

    # Assert WS response.
    content = tu.assert_ws_response(_URL_RETRIEVE, response)
    assert 'issue' in content

    # Assert WS response content.
    issue = content['issue']
    for key in {'closedBy', 'createdBy', 'updatedBy', 'dateClosed', 'dateCreated', 'dateUpdated'}:
        assert key in issue
        if key not in {'closedBy', 'dateClosed'}:
            assert issue[key] is not None
    for attr in ISSUE.keys():
        if attr == 'facets':
            for facet_type, facet_values in issue['facets'].items():
                assert set(ISSUE['facets'][facet_type]) == set(facet_values)
        elif attr not in {'datasets', 'materials'}:
            assert issue[attr] == ISSUE[attr], \
                   "{} :: {} :: {}".format(attr, issue[attr], ISSUE[attr])
        elif attr in issue:
            assert sorted(issue[attr]) == sorted(ISSUE[attr]), \
                   "{} :: {} :: {}".format(attr, sorted(issue[attr]), sorted(ISSUE[attr]))


def test_update():
    """ERRATA :: WS :: Postive Test :: Update issue.

    """
    # Update test issue.
    ISSUE['status'] = constants.STATUS_RESOLVED
    ISSUE['dateUpdated'] = unicode(dt.datetime.utcnow())
    ISSUE['datasets'] = random.sample(ISSUE_DATASETS, 5)

    # Invoke WS endpoint.
    response = requests.post(
        _URL_UPDATE,
        data=json.dumps(ISSUE),
        headers={'Content-Type': 'application/json'},
        auth=tu.get_credentials()
        )

    # Assert WS response.
    tu.assert_ws_response(_URL_UPDATE, response)


def _test_update_retrieve():
    """ERRATA :: WS :: Postive Test :: Retrieve updated issue.

    """
    # Invoke WS endpoint.
    response = requests.get(_URL_RETRIEVE)

    # Assert WS response.
    content = tu.assert_ws_response(_URL_RETRIEVE, response)

    # Assert WS response content.
    issue = content['issue']
    assert issue['status'] == ISSUE['status']
    assert issue['dateUpdated'] == ISSUE['dateUpdated']
    assert issue['updatedBy'] is not None
    # assert len(content['issue']['datasets']) == 5


def _test_close():
    """ERRATA :: WS :: Postive Test :: Close issue.

    """
    # Invoke WS endpoint.
    response = requests.post(_URL_CLOSE, auth=tu.get_credentials())

    # Assert WS response.
    tu.assert_ws_response(_URL_CLOSE, response)


def _test_close_retrieve():
    """ERRATA :: WS :: Postive Test :: Retrieve closed issue.

    """
    # Invoke WS endpoint.
    response = requests.get(_URL_RETRIEVE)

    # Assert WS response.
    content = tu.assert_ws_response(_URL_RETRIEVE, response)

    # Assert WS response content.
    issue = content['issue']
    assert issue['dateClosed'] is not None
    assert issue['closedBy'] is not None
    assert issue['status'] == constants.STATUS_RESOLVED
