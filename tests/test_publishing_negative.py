import json
import urllib
import uuid

import requests

import pyessv
from pyessv._utils.compat import basestring
from errata_ws.utils import factory
from errata_ws.utils.constants import *
from tests import utils as tu


# Test endpoint: create issue.
_URL_CREATE = "{}/1/issue/create".format(tu.BASE_URL)

# Test endpoint: update issue.
_URL_UPDATE = "{}/1/issue/update".format(tu.BASE_URL)


def test_publishing():
    """ERRATA :: WS :: PUBLISHING :: issue (-ve).

    """
    for test_type in ['create', 'update']:
        # Simple field tests.
        for field in [
            'description',
            'project',
            'severity',
            'status',
            'title',
            'uid'
            ]:
            yield _do_test(test_type, _callback_01, field, "is not a string")

        # Constrained field tests.
        for field in [
            'project',
            'severity',
            'status',
            'uid'
            ]:
            yield _do_test(test_type, _callback_02, field, "is invalid string value")

        # Array field tests.
        for field in [
            'datasets',
            'materials',
            'urls'
            ]:
            yield _do_test(test_type, _callback_02, field, "is not an array")
            yield _do_test(test_type, _callback_03, field, "is invalid array [contains non-string values]")
            yield _do_test(test_type, _callback_04, field, "is invalid array [contains invalid item]")

        # Dataset identifier tests.
        yield _do_test(test_type, _callback_05, 'datasets', "with invalid DRS elements")
        yield _do_test(test_type, _callback_06, 'datasets', "with multiple institutes")

    # More specialized tests.
    yield _do_test('update', _callback_07, 'uid', "does not match an existing issue")
    for field in {'project', 'title'}:
        yield _do_test('update', _callback_08, field, "is an immutable attribute")
    yield _do_test('update', _callback_09, 'status', "change error")


def _do_test(test_type, callback, field, description):
    """Executes unit test.

    """
    issue = factory.create_issue_dict()

    def _do_create():
        """Performs a create issue test."""
        callback(issue, field)
        _assert_bad_ws_response(requests.post(
            _URL_CREATE,
            data=json.dumps(issue),
            auth=tu.get_credentials()
            ))


    def _do_update():
        """Performs an update issue test."""
        requests.post(
            _URL_CREATE,
            data=json.dumps(issue),
            auth=tu.get_credentials()
            )
        callback(issue, field)
        _assert_bad_ws_response(requests.post(
            _URL_UPDATE,
            data=json.dumps(issue),
            auth=tu.get_credentials()
            ))

    func = _do_create if test_type == 'create' else _do_update
    func.description = "ERRATA :: WS :: PUBLISHING :: {} issue (-ve) :: {} {}".format(test_type, field, description)

    return func


def _callback_01(issue, field):
    """Set field value to a non string value."""
    issue[field] = 123


def _callback_02(issue, field):
    """Set field value to an invalid string value."""
    issue[field] = "invalid-value"


def _callback_03(issue, field):
    """Set array field value to a non-string array."""
    issue[field] = [123]


def _callback_04(issue, field):
    """Set URL field value to an array with an invalid url."""
    issue[field] = ["an-invalid-item.png"]


def _callback_05(issue, _):
    """Set dataset identifer to an invalid value."""
    for idx, identifier in enumerate(issue['datasets']):
        parts = identifier.split('.')
        parts[2] = 'xxxxx'
        issue['datasets'][idx] = '.'.join(parts)


def _callback_06(issue, _):
    """Set dataset identifers so that multiple institutes are repesented."""
    identifier = issue['datasets'][0]
    parts = identifier.split('.')
    project = parts[0].lower()
    if project in {'cordex', }:
        parts[3] = 'mohc'
    elif project in {'cmip5', 'cmip6'}:
        parts[2] = 'mohc'
    issue['datasets'][0] = '.'.join(parts)


def _callback_07(issue, _):
    """Set issue uid so that update will fail."""
    issue['uid'] = unicode(uuid.uuid4())


def _callback_08(issue, field):
    """Set immutable field."""
    if field == 'title':
        issue['title'] = unicode(uuid.uuid4())
    elif field == 'project':
        project = issue['project']
        while project == issue['project']:
            issue['project'] = pyessv.load_random('esdoc:errata:project')


def _callback_09(issue, _):
    """Set status field to an invalid value."""
    issue['status'] = ISSUE_STATUS_NEW


def _assert_bad_ws_response(response):
    """Asserts a response received from web-service.

    """
    # WS response HTTP status code.
    assert response.status_code == requests.codes.BAD_REQUEST, \
           "invalid response code: actual={} :: expected={}".format(response.status_code, requests.codes.BAD_REQUEST)

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
    for field, test_type in {('errorCode', int), ('errorMessage', basestring), ('errorType', basestring), ('errorField', basestring)}:
        assert field in obj
        assert isinstance(obj[field], test_type), "{}:{}".format(obj[field], field)
