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

from errata.utils.constants import INSTITUTION_ID
from errata.utils.constants import MIP_ERA
from errata.utils.constants import SEVERITY
from errata.utils.constants import STATUS
from errata.utils.constants_test import ISSUE


# Set of target urls.
_URL = os.getenv("ERRATA_API")
_URL_CREATE = "{}/1/issue/create".format(_URL)
_URL_SEARCH_SETUP = "{}/1/issue/search-setup".format(_URL)
_URL_SEARCH = "{}/1/issue/search".format(_URL)
_URL_SEARCH_PARAMS = "?institution_id={}&mip_era={}&severity={}&status={}"


def test_search_setup():
    """ERRATA :: WS :: Postive Test :: Search setup.

    """
    # Invoke WS endpoint.
    response = requests.get(_URL_SEARCH_SETUP)

    # Assert WS response.
    response = _assert_ws_response(_URL_SEARCH_SETUP, response)

    assert "institution_id" in response
    assert "mip_era" in response
    assert "severity" in response
    assert "status" in response



def test_search():
    """ERRATA :: WS :: Postive Test :: Search execution.

    """
    # Initialise expected results.
    expected = collections.defaultdict(int)

    # Publish test issues.
    for _ in range(50):
        # ... create issue;
        issue = ISSUE.copy()
        issue['uid'] = unicode(uuid.uuid4())
        issue['institution_id'] = random.choice(INSTITUTION_ID)['key']
        issue['mip_era'] = random.choice(MIP_ERA)['key']
        issue['severity'] = random.choice(SEVERITY)['key']
        issue['status'] = random.choice(STATUS)['key']

        # ... update expected results;
        expected[(issue['institution_id'], issue['mip_era'], issue['severity'], issue['status'])] += 1

        # .... publish issue.
        response = requests.post(
            _URL_CREATE,
            data=json.dumps(issue),
            headers={'Content-Type': 'application/json'}
            )

    # Perform searches:
    for institution_id, mip_era, severity, status in expected:
        # ... invoke WS;
        url = "{}{}".format(_URL_SEARCH, _URL_SEARCH_PARAMS.format(
            institution_id,
            mip_era,
            severity,
            status
            ))
        response = requests.get(url)

        # Assert WS response.
        response = _assert_ws_response(url, response)

        # Assert search return at least expected total.
        assert expected[institution_id, mip_era, severity, status] <= response['total']


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
