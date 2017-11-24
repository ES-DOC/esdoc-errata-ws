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
from errata.utils import factory
from tests import utils as tu



# Test issue.
_ISSUE = factory.create_issue_dict()

# Test endpoint: close issue.
_URL_CLOSE = '{}/1/issue/close?'.format(tu.BASE_URL)
_URL_CLOSE += urllib.urlencode({
    'uid': _ISSUE['uid'],
    'status': constants.STATUS_RESOLVED
    })

# Test endpoint: create issue.
_URL_CREATE = "{}/1/issue/create".format(tu.BASE_URL)

# Test endpoint: retrieve issue.
_URL_RETRIEVE = '{}/1/issue/retrieve?'.format(tu.BASE_URL)
_URL_RETRIEVE += urllib.urlencode({
    'uid': _ISSUE['uid']
    })

# Test endpoint: update issue.
_URL_UPDATE = "{}/1/issue/update".format(tu.BASE_URL)


def test_create():
    """ERRATA :: WS :: PUBLISHING :: create issue.

    """
    # Invoke WS endpoint.
    response = requests.post(
        _URL_CREATE,
        data=json.dumps(_ISSUE),
        headers={'Content-Type': 'application/json'},
        auth=tu.get_credentials()
        )

    # Assert WS response.
    tu.assert_ws_response(_URL_CREATE, response)


def test_create_retrieve():
    """ERRATA :: WS :: PUBLISHING :: retrieve created issue.

    """
    # Invoke WS endpoint.
    response = requests.get(_URL_RETRIEVE)

    # Assert WS response.
    content = tu.assert_ws_response(_URL_RETRIEVE, response)

    # Assert content.
    assert 'issue' in content
    issue = content['issue']

    # Assert core info.
    for attr in [i for i in _ISSUE.keys() if i != 'facets']:
        if attr not in {'datasets', 'materials'}:
            assert issue[attr] == _ISSUE[attr], "{}::{}::{}".format(attr, issue[attr], _ISSUE[attr])
        elif attr in issue:
            assert sorted(issue[attr]) == sorted(_ISSUE[attr]), "{}::{}::{}".format(attr, sorted(issue[attr]), sorted(_ISSUE[attr]))

    # Assert tracking info.
    _assert_tracking_info(issue)


def test_update():
    """ERRATA :: WS :: PUBLISHING :: update issue.

    """
    # Update test issue.
    _ISSUE['status'] = constants.STATUS_RESOLVED
    _ISSUE['datasets'] = factory.get_datasets(_ISSUE['project'], random.sample(_ISSUE['datasets'], 2))

    # Invoke WS endpoint.
    response = requests.post(
        _URL_UPDATE,
        data=json.dumps(_ISSUE),
        headers={'Content-Type': 'application/json'},
        auth=tu.get_credentials()
        )

    # Assert WS response.
    tu.assert_ws_response(_URL_UPDATE, response)


def test_update_retrieve():
    """ERRATA :: WS :: PUBLISHING :: retrieve updated issue.

    """
    # Invoke WS endpoint.
    response = requests.get(_URL_RETRIEVE)

    # Assert WS response.
    content = tu.assert_ws_response(_URL_RETRIEVE, response)

    # Assert content.
    assert 'issue' in content
    issue = content['issue']

    # Assert core info.
    assert issue['status'] == _ISSUE['status']

    # Assert tracking info.
    assert issue['updatedDate'] is not None
    _assert_tracking_info(issue)


def test_close():
    """ERRATA :: WS :: PUBLISHING :: close issue.

    """
    # Invoke WS endpoint.
    response = requests.post(_URL_CLOSE, auth=tu.get_credentials())

    # Assert WS response.
    tu.assert_ws_response(_URL_CLOSE, response)


def test_close_retrieve():
    """ERRATA :: WS :: PUBLISHING :: retrieve closed issue.

    """
    # Invoke WS endpoint.
    response = requests.get(_URL_RETRIEVE)

    # Assert WS response.
    content = tu.assert_ws_response(_URL_RETRIEVE, response)

    # Assert content.
    assert 'issue' in content
    issue = content['issue']

    # Assert core info.
    assert issue['status'] == constants.STATUS_RESOLVED

    # Assert tracking info.
    assert issue['closedDate'] is not None
    _assert_tracking_info(issue)


def _assert_tracking_info(issue):
    """Performs assertions over issue tracking information.

    """
    for user_field, date_field in {
        ('closedBy', 'closedDate'),
        ('createdBy', 'createdDate'),
        ('updatedBy', 'updatedDate')
        }:
        assert user_field in issue
        assert date_field in issue
        if user_field == 'createdBy':
            assert issue[user_field] is not None
        if date_field == 'createdDate':
            assert issue[date_field] is not None
        if issue[user_field] is not None:
            assert issue[date_field] is not None
