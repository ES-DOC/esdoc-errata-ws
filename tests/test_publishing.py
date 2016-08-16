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
import uuid

import requests

from errata.utils import constants



# Test issue.
_ISSUE = {
    'description': unicode(uuid.uuid4()),
    'institute': constants.INSTITUTE_IPSL,
    'materials': [
        "http://errata.ipsl.upmc.fr/static/images_errata/time.jpg",
        "http://errata.ipsl.upmc.fr/static/images_errata/time5.jpg"
    ],
    'models': [],
    'severity': constants.SEVERITY_LOW,
    'project': u"TEST",
    'title': unicode(uuid.uuid4()),
    'id': unicode(uuid.uuid4()),
    'url': u"http://errata.ipsl.upmc.fr/issue/1",
    'workflow': constants.WORKFLOW_NEW,
    'datasets': [
        "cmip5.output1.IPSL.IPSL-CM5A-LR.1pctCO2.yr.ocnBgchem.Oyr.r2i1p1#20161010",
        "cmip5.output1.IPSL.IPSL-CM5A-LR.1pctCO2.yr.ocnBgchem.Oyr.r1i1p1#20161010",
        "cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r10i1p1#20110922",
        "cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r11i1p1#20110901",
        "cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r12i1p1#20110901",
        "cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r1i1p1#20110901",
        "cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r1i1p1#20130322",
        "cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r2i1p1#20110901",
        "cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r3i1p1#20110901",
        "cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r4i1p1#20110901",
        "cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r6i1p1#20110901",
        "cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r7i1p1#20110901",
        "cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r8i1p1#20110901",
        "cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r9i1p1#20110901"
        ]
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



def _assert_ws_response(
    url,
    response,
    status_code=requests.codes.OK,
    expected_content=None):
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

    # WS response processing status.
    assert 'status' in content
    assert content['status'] == 0 if status_code == requests.codes.OK else -1

    # WS response content.
    if expected_content is not None:
        assert content == expected_content

    return content


def test_create():
    """ERRATA :: WS :: Test creating an issue.

    """
    # Invoke WS endpoint.
    url = _URL_CREATE
    response = requests.post(
        url,
        data=json.dumps(_ISSUE),
        headers=_REQUEST_HEADERS[_URL_CREATE]
        )

    # Assert WS response.
    _assert_ws_response(url, response, expected_content={'status': 0})


def test_retrieve():
    """ERRATA :: WS :: Test retrieving an issue.

    """
    # Invoke WS endpoint.
    response = requests.get(_URL_RETRIEVE)

    # Assert WS response.
    content = _assert_ws_response(_URL_RETRIEVE, response)

    # Assert WS response content.
    assert 'issue' in content
    for attr in [i for i in _ISSUE.keys() if i != 'models']:
        try:
            assert sorted(content['issue'][attr]) == sorted(_ISSUE[attr])
        except TypeError:
            assert content['issue'][attr] == _ISSUE[attr]


def test_close():
    """ERRATA :: WS :: Test closing an issue.

    """
    # Invoke WS endpoint.
    response = requests.post(_URL_CLOSE)

    # Assert WS response.
    _assert_ws_response(_URL_CLOSE, response)


def test_update():
    """ERRATA :: WS :: Test updating an issue.

    """
    # Update test issue.
    _ISSUE['severity'] = constants.SEVERITY_MEDIUM
    _ISSUE['date_updated'] = unicode(dt.datetime.utcnow())

    # Invoke WS endpoint.
    response = requests.post(
        _URL_UPDATE,
        data=json.dumps(_ISSUE),
        headers=_REQUEST_HEADERS[_URL_UPDATE]
        )

    # Assert WS response.
    _assert_ws_response(_URL_UPDATE, response, expected_content={'status': 0})
