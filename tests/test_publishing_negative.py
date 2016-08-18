# -*- coding: utf-8 -*-

"""
.. module:: test_publishing_negative.py

   :license: GPL / CeCILL
   :platform: Unix, Windows
   :synopsis: Executes web-service publishing endpoint tests (negative).

.. moduleauthor:: Earth System Documentation (ES-DOC) <dev@es-doc.org>

"""
import json
import os

import nose
import requests

from errata.utils.constants import ISSUE



# Set of target urls.
_URL = os.getenv("ERRATA_API")
_URL_CREATE = "{}/1/issue/create".format(_URL)
_URL_UPDATE = "{}/1/issue/update".format(_URL)
_URL_RETRIEVE = "{}/1/issue/retrieve?uid={}".format(_URL, ISSUE['uid'])
_URL_CLOSE = "{}/1/issue/close?uid={}".format(_URL, ISSUE['uid'])

# Set of target url request headers.
_REQUEST_HEADERS = {
    _URL_CREATE:  {'Content-Type': 'application/json'},
    _URL_UPDATE:  {'Content-Type': 'application/json'}
}


def test_create_invalid():
    """ERRATA :: WS :: Test creating an issue - invalid id.

    """
    def _do_test(issue, attr, description):
        """Executes create issue unit test.

        """
        def _do():
            # Invoke WS endpoint.
            url = _URL_CREATE
            response = requests.post(
                url,
                data=json.dumps(issue),
                headers=_REQUEST_HEADERS[_URL_CREATE]
                )

            # Assert WS response.
            _assert_ws_response(url, response, requests.codes.BAD_REQUEST)

        _do.description = "ERRATA :: WS :: Negative test :: Create Issue :: {} {}".format(attr, description)

        return _do


    # Test string properties:
    for attr in ['description', 'uid', 'institute', 'project', 'severity', 'url', 'workflow']:
        issue = ISSUE.copy()
        # ... non-text values are invalid;
        issue[attr] = 123
        yield _do_test(issue, attr, "is not a string")
        # ... constrained values;
        if attr != 'description':
            issue[attr] = "invalid-value"
            yield _do_test(issue, attr, "is invalid string value")


    # Test array properties:
    for attr in {'datasets', 'materials', 'models'}:
        issue = ISSUE.copy()
        # ... non-array values are invalid;
        issue[attr] = "invalid-value"
        yield _do_test(issue, attr, "is not an array")
        # ... arrays must contain only string values;
        issue[attr] = [123]
        yield _do_test(issue, attr, "is invalid array [contains non-string values]")
        # ... datasets / materials are further validated against a regex;
        if attr != 'models':
            issue[attr] = ["an-invalid-item"]
            yield _do_test(issue, attr, "is invalid array [contains invalid item]")


@nose.tools.nottest
def test_create_invalid_title():
    """ERRATA :: WS :: Test creating an issue - invalid title.

    """
    raise NotImplementedError()


def _assert_ws_response(
    url,
    response,
    expected_status_code=requests.codes.OK,
    expected_content=None):
    """Asserts a response received from web-service.

    """
    # WS url.
    assert response.url == url

    # WS response HTTP status code.
    assert response.status_code == expected_status_code, \
           "invalid response code: actual={} :: expected={}".format(response.status_code, expected_status_code)

    # WS response = unicode.
    assert isinstance(response.text, unicode)

    # WS response has no cookies.
    assert len(response.cookies) == 0

    # WS response encoding = utf-8.
    if response.status_code == requests.codes.OK:
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

    # Verify WS response content:
    if response.status_code == requests.codes.OK:
        # ... must be JSON deserializable
        content = response.json()
        assert isinstance(content, dict)

        # ... must contain service status
        # WS response processing status.
        assert 'status' in content
        assert content['status'] == 0 if expected_status_code == requests.codes.OK else -1

        # WS response content.
        if expected_content is not None:
            assert content == expected_content

        return content
