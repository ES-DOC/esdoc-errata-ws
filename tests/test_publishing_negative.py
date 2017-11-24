# -*- coding: utf-8 -*-

"""
.. module:: test_publishing_negative.py

   :license: GPL / CeCILL
   :platform: Unix, Windows
   :synopsis: Executes web-service publishing endpoint tests (negative).

.. moduleauthor:: Earth System Documentation (ES-DOC) <dev@es-doc.org>

"""
import json
import urllib

import requests

from pyessv._utils.compat import basestring
from errata.utils import factory
from tests import utils as tu



D = '''
{
    "project": "cordex", 
    "status": "new", 
    "datasets": [
        "cordex.output.cas-44.ipsl-ineris.cnrm-cerfacs-cnrm-cm5.historical.r12i1p1.wrf350i.v1.3hr.zmla#v20180101", 
        "cordex.output.aus-44.ipsl-ineris.miroc-miroc5.rcp45.r12i1p1.promes.v1.sem.rlds#v20180101", 
        "cordex.output.eur-44.ipsl-ineris.mpi-m-mpi-esm-mr.rcp45.r12i1p1.wrf331.v1.mon.sfcwindmax#v20180101", 
        "cordex.output.mna-22.ipsl-ineris.mpi-m-mpi-esm-lr.rcp45.r12i1p1.remo2009.v1.sem.va300#v20180101", 
        "cordex.output.eas-44i.ipsl-ineris.ecmwf-eraint.rcp60.r12i1p1.hadrm3p.v1.mon.ua600#v20180101"
    ], 
    "description": "310d649e-3153-4d4f-b7e8-b72b59a3a346", 
    "urls": [
        "https://es-doc.org/cmip6-dataset-errata"
    ], 
    "title": "0bc926c5-9709-4baa-9027-ffe7fb763215", 
    "uid": "113456ef-e8a3-4d60-8536-1aab891d31b5", 
    "severity": "medium", 
    "materials": [
        "https://test-errata.es-doc.org/media/img/materials/material-01.png", 
        "https://test-errata.es-doc.org/media/img/materials/material-02.png", 
        "https://test-errata.es-doc.org/media/img/materials/material-03.png", 
        "https://test-errata.es-doc.org/media/img/materials/material-04.png", 
        "https://test-errata.es-doc.org/media/img/materials/material-05.png"
    ]
}
'''

# Test issue.
_ISSUE = factory.create_issue_dict()
# print json.dumps(_ISSUE, indent=4)

# Test endpoint: create issue.
_URL_CREATE = "{}/1/issue/create".format(tu.BASE_URL)

# Test endpoint: retrieve issue.
_URL_RETRIEVE = '{}/1/issue/retrieve?'.format(tu.BASE_URL)
_URL_RETRIEVE += urllib.urlencode({
    'uid': _ISSUE['uid']
    })

# Test endpoint: update issue.
_URL_UPDATE = "{}/1/issue/update".format(tu.BASE_URL)


def test_create_invalid():
    """ERRATA :: WS :: Test creating an issue - invalid id.

    """
    # Test string properties:
    for attr in [
        'description',
        'project',
        'severity',
        'status',
        'title',
        'uid'
        ]:
        # ... test invalid value;
        issue = _ISSUE.copy()
        issue[attr] = 123
        yield _do_test(issue, attr, "is not a string")

        # ... test constrained values;
        if attr not in {'description', 'title'}:
            issue[attr] = "invalid-value"
            yield _do_test(issue, attr, "is invalid string value")


    # Test array properties:
    for attr in {
        'datasets',
        'materials',
        'urls'
        }:
        # ... test invalid value
        issue = _ISSUE.copy()
        issue[attr] = "invalid-value"
        yield _do_test(issue, attr, "is not an array")

        # ... arrays must contain only string values;
        issue[attr] = [123]
        yield _do_test(issue, attr, "is invalid array [contains non-string values]")

        # ... array values are further validated;
        issue[attr] = ["an-invalid-item.png"]
        yield _do_test(issue, attr, "is invalid array [contains invalid item]")


def test_create_invalid_datasets():
    """ERRATA :: WS :: Test creating an issue - invalid title.

    """
    def _convert(identifier):
        parts = identifier.split('.')
        parts[2] = 'xxxxx'
        return '.'.join(parts)

    issue = _ISSUE.copy()
    issue['datasets'] = [_convert(i) for i in issue['datasets']]
    yield _do_test(issue, 'datasets', "is invalid array [contains invalid datasets]")


def test_create_invalid_title():
    """ERRATA :: WS :: Test creating an issue - invalid title.

    """
    pass


def _do_test(issue, attr, description):
    """Executes create issue unit test.

    """
    def _do():
        response = requests.post(
            _URL_CREATE,
            data=json.dumps(issue),
            headers={'Content-Type': 'application/json'},
            auth=tu.get_credentials()
            )
        _assert_ws_response(_URL_CREATE, response)

    _do.description = "ERRATA :: WS :: PUBLISHING :: create issue (-ve) :: {} {}".format(attr, description)

    return _do


def _assert_ws_response(
    url,
    response,
    expected_status_code=requests.codes.BAD_REQUEST,
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

    # WS response headers.
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

    # WS JSON response.
    obj = json.loads(response.text)
    assert isinstance(obj, dict)
    for field, typeof in {('errorCode', int), ('errorMessage', basestring), ('errorType', basestring), ('errorField', basestring)}:
        assert field in obj
        assert isinstance(obj[field], typeof), "{}:{}".format(obj[field], field)
