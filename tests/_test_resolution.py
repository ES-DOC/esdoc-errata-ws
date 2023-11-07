import json
import os
import urllib

import requests

from errata_ws.utils.constants import *



# Set of target urls.
_URL = os.getenv("ERRATA_API")
_URL_CREATE = "{}/1/issue/create".format(_URL)
_URL_RESOLVE = "{}/1/resolve/issue?{}"

_URL_RESOLVE_DATASET = "{}/1/resolve/issue?facetType=dataset&{}".format(
    _URL, urllib.urlencode({'facetID': ISSUE['datasets'][0]}))
_URL_RESOLVE_MODEL = "{}/1/resolve/issue?facetType=model&{}".format(
    _URL, urllib.urlencode({'facetID': ISSUE['models'][0]}))


def test_resolve():
    """ERRATA :: WS :: Resolve issue(s) from facet id.

    """
    def _do(facet_type):
        """Executes create issue unit test.

        """
        # Publish test issue.
        _publish_issue()

        # Invoke WS endpoint.
        endpoint = _URL_RESOLVE.format(_URL, urllib.urlencode({
            'facetType': facet_type,
            'facetID': ISSUE["{}s".format(facet_type)][0]
        }))
        response = requests.get(endpoint)

        # Perform standard asserts.
        content = _assert_ws_response(endpoint, response)

        # Perform specific asserts.
        assert ISSUE['uid'] in content['issueIdentifiers']
        assert content['facetID'] == ISSUE["{}s".format(facet_type)][0]
        assert content['facetType'] == facet_type
        assert content['count'] >= 1
        assert content['count'] == len(content['issueIdentifiers'])


    for facet_type in CORE_FACET_TYPESET:
        _do.description = "ERRATA :: WS :: Postive test :: Resolve Issue from {}".format(facet_type)

        yield _do, facet_type


def _publish_issue():
    """Publishes a test issue.

    """
    requests.post(
        _URL_CREATE,
        data=json.dumps(ISSUE),
        headers={'Content-Type': 'application/json'}
        )


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
