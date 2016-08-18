# -*- coding: utf-8 -*-

"""
.. module:: test_resolution.py

   :license: GPL / CeCILL
   :platform: Unix, Windows
   :synopsis: Executes web-service resolution endpoint tests.

.. moduleauthor:: Earth System Documentation (ES-DOC) <dev@es-doc.org>

"""
import json
import os
import urllib

import requests

from errata.utils.constants import ISSUE



# Set of target urls.
_URL = os.getenv("ERRATA_API")
_URL_CREATE = "{}/1/issue/create".format(_URL)
_URL_RESOLVE_DATASET = "{}/1/resolve/issue-from-dataset?{}".format(
    _URL, urllib.urlencode({'dataset': ISSUE['datasets'][0]}))
_URL_RESOLVE_MODEL = "{}/1/resolve/issue-from-model?{}".format(
    _URL, urllib.urlencode({'model': ISSUE['models'][0]}))


def _publish_issue():
    """Publishes a test issue.

    """
    # Invoke WS endpoint.
    url = _URL_CREATE
    response = requests.post(
        url,
        data=json.dumps(ISSUE),
        headers={'Content-Type': 'application/json'}
        )


def test_resolve_dataset():
    """ERRATA :: WS :: Postive Test :: Resolve issue(s) from dataset id.

    """
    # Publish test issue.
    _publish_issue()

    # Invoke WS endpoint.
    response = requests.get(_URL_RESOLVE_DATASET)

    # Perform standard asserts.
    content = _assert_ws_response(_URL_RESOLVE_DATASET, response)

    # Perform specific asserts.
    assert ISSUE['uid'] in content['issueIdentifiers']
    assert  ISSUE['datasets'][0] == content['datasetID']
    assert  content['count'] >= 1
    assert  content['count'] == len(content['issueIdentifiers'])


def test_resolve_model():
    """ERRATA :: WS :: Postive Test :: Resolve issue(s) from model id.

    """
    # Publish test issue.
    _publish_issue()

    # Invoke WS endpoint.
    response = requests.get(_URL_RESOLVE_MODEL)

    # Perform standard asserts.
    content = _assert_ws_response(_URL_RESOLVE_MODEL, response)

    # Perform specific asserts.
    assert ISSUE['uid'] in content['issueIdentifiers']
    assert  ISSUE['models'][0] == content['modelID']
    assert  content['count'] >= 1
    assert  content['count'] == len(content['issueIdentifiers'])


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
    assert response.status_code == status_code

    # WS response = unicode.
    assert isinstance(response.text, unicode)

    # WS response has no cookies.
    assert len(response.cookies) == 0

    # WS response encoding = utf-8.
    assert response.encoding == u'utf-8'

    # WS respponse headers.
    assert len(response.headers) >= 5
    for header in {
        'Content-Length',
        'Content-Type',
        'Date',
        'Server',
        'Vary'
        }:
        assert header in response.headers

    # WS response history is empty (i.e. no intermediate servers).
    assert len(response.history) == 0
    assert response.is_permanent_redirect == False
    assert response.is_redirect == False
    assert len(response.links) == 0

    # WS response content must be JSON.
    content = response.json()
    assert isinstance(content, dict)

    # WS response content.
    if expected_content is not None:
        assert content == expected_content

    return content
