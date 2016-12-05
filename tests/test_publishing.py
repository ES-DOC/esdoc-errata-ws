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
import urllib

import requests

from errata.utils import constants
from errata.utils.constants_test import ISSUE



# Set of target urls.
_URL = os.getenv("ERRATA_API")
_URL_CLOSE = "{}/1/issue/close?{}".format(
    _URL, urllib.urlencode({
        'uid': ISSUE['uid'],
        'status': constants.STATUS_RESOLVED
        }))
_URL_CREATE = "{}/1/issue/create".format(_URL)
_URL_RETRIEVE = "{}/1/issue/retrieve?{}".format(
    _URL, urllib.urlencode({
        'uid': ISSUE['uid']
        }))
_URL_UPDATE = "{}/1/issue/update".format(_URL)


def test_create():
    """ERRATA :: WS :: Postive Test :: Create issue.

    """
    # Invoke WS endpoint.
    response = requests.post(
        _URL_CREATE,
        data=json.dumps(ISSUE),
        headers={'Content-Type': 'application/json'},
        auth=_get_ws_credentials()
        )

    # Assert WS response.
    _assert_ws_response(_URL_CREATE, response)


def test_retrieve():
    """ERRATA :: WS :: Postive Test :: Retrieve issue.

    """
    # Invoke WS endpoint.
    response = requests.get(_URL_RETRIEVE)

    # Assert WS response.
    content = _assert_ws_response(_URL_RETRIEVE, response)

    # Assert WS response content.
    assert 'issue' in content
    assert content['issue']['createdBy'] is not None
    for attr in ISSUE.keys():
        if attr in {'datasets', 'materials', 'models', 'variables', 'experiments'}:
            assert sorted(content['issue'][attr]) == sorted(ISSUE[attr])
        else:
            try:
                assert content['issue'][attr] == ISSUE[attr]
            except KeyError:
                print attr


def test_update():
    """ERRATA :: WS :: Postive Test :: Update issue.

    """
    # Update test issue.
    ISSUE['status'] = constants.STATUS_RESOLVED
    ISSUE['dateUpdated'] = unicode(dt.datetime.utcnow())

    # Invoke WS endpoint.
    response = requests.post(
        _URL_UPDATE,
        data=json.dumps(ISSUE),
        headers={'Content-Type': 'application/json'},
        auth=_get_ws_credentials()
        )

    # Assert WS response.
    _assert_ws_response(_URL_UPDATE, response)


def test_update_retrieve():
    """ERRATA :: WS :: Postive Test :: Retrieve updated issue.

    """
    # Invoke WS endpoint.
    response = requests.get(_URL_RETRIEVE)

    # Assert WS response.
    content = _assert_ws_response(_URL_RETRIEVE, response)

    # Assert WS response content.
    assert content['issue']['status'] == ISSUE['status']
    assert content['issue']['dateUpdated'] == ISSUE['dateUpdated']
    assert content['issue']['updatedBy'] is not None


def test_close():
    """ERRATA :: WS :: Postive Test :: Close issue.

    """
    # Invoke WS endpoint.
    response = requests.post(_URL_CLOSE, auth=_get_ws_credentials())

    # Assert WS response.
    _assert_ws_response(_URL_CLOSE, response)


def test_close_retrieve():
    """ERRATA :: WS :: Postive Test :: Retrieve closed issue.

    """
    # Invoke WS endpoint.
    response = requests.get(_URL_RETRIEVE)

    # Assert WS response.
    content = _assert_ws_response(_URL_RETRIEVE, response)

    # Assert WS response content.
    assert content['issue']['dateClosed'] is not None
    assert content['issue']['closedBy'] is not None
    assert content['issue']['status'] == constants.STATUS_RESOLVED


def _get_ws_credentials():
    """Returns credentials to be passed to web-service.

    """
    return os.getenv('ERRATA_GITHUB_USER_NAME'), \
           os.getenv('ERRATA_GITHUB_ACCESS_TOKEN')


def _assert_ws_response(
    url,
    response,
    status_code=requests.codes.OK,
    expected_content=None
    ):
    """Asserts a response received from web-service.

    """
    # WS url.
    assert response.url == url

    # WS response HTTP status code.
    assert response.status_code == status_code, response.status_code

    # WS response = unicode.
    assert isinstance(response.text, unicode)

    # WS response has no cookies.
    assert len(response.cookies) == 0

    # WS response history is empty (i.e. no intermediate servers).
    assert len(response.history) == 0
    assert response.is_permanent_redirect == False
    assert response.is_redirect == False
    assert len(response.links) == 0

    # Default WS respponse headers.
    assert len(response.headers) >= 3
    for header in {
        'Content-Length',
        'Content-Type',
        'Date',
        'Server',
        'Vary'
        }:
        assert header in response.headers

    # WS response content must be utf-8 encoded JSON.
    if response.text:
        assert response.encoding == u'utf-8'
        content = response.json()
        assert isinstance(content, dict)

        # WS response content.
        if expected_content is not None:
            assert content == expected_content

        return content
