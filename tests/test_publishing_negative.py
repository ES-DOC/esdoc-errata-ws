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
import uuid

import nose
import requests

from errata.utils import constants



# Test issue.
_ISSUE = {
    'datasets': [
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.1pctCO2.yr.ocnBgchem.Oyr.r2i1p1#20161010",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.1pctCO2.yr.ocnBgchem.Oyr.r1i1p1#20161010",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r10i1p1#20110922",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r11i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r12i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r1i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r1i1p1#20130322",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r2i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r3i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r4i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r6i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r7i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r8i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r9i1p1#20110901"
        ],
    'description': unicode(uuid.uuid4()),
    'id': unicode(uuid.uuid4()),
    'institute': constants.INSTITUTE_IPSL,
    'materials': [
        u"http://errata.ipsl.upmc.fr/static/images_errata/time.jpg",
        u"http://errata.ipsl.upmc.fr/static/images_errata/time5.jpg"
        ],
    'models': [],
    'project': constants.PROJECT_TEST,
    'severity': constants.SEVERITY_LOW,
    'title': unicode(uuid.uuid4()),
    'url': u"http://errata.ipsl.upmc.fr/issue/1",
    'workflow': constants.WORKFLOW_NEW
    }

# Set of target urls.
_URL = os.getenv("ERRATA_API")
_URL_CREATE = "{}/1/issue/create".format(_URL)
_URL_UPDATE = "{}/1/issue/update".format(_URL)
_URL_RETRIEVE = "{}/1/issue/retrieve?uid={}".format(_URL, _ISSUE['id'])
_URL_CLOSE = "{}/1/issue/close?uid={}".format(_URL, _ISSUE['id'])

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
    for attr in ['description', 'id', 'institute', 'project', 'severity', 'url', 'workflow']:
        issue = _ISSUE.copy()
        # ... non-text values are invalid;
        issue[attr] = 123
        yield _do_test(issue, attr, "is not a string")
        # ... constrained values;
        if attr != 'description':
            issue[attr] = "invalid-value"
            yield _do_test(issue, attr, "is invalid string value")


    # Test array properties:
    for attr in {'datasets', 'materials', 'models'}:
        issue = _ISSUE.copy()
        # ... non-array values are invalid;
        issue[attr] = "invalid-value"
        yield _do_test(issue, attr, "is not an array")
        issue[attr] = 123
        yield _do_test(issue, attr, "is invalid array [contains a non-string item]")
        # ... all array items must be valid;
        if attr != 'description':
            issue[attr] = ["an-invalid-item"]
            yield _do_test(issue, attr, "is invalid array [contains invalid item]")


@nose.tools.nottest
def test_create_invalid_title():
    """ERRATA :: WS :: Test creating an issue - invalid title.

    """
    pass


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
