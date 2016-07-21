# -*- coding: utf-8 -*-
"""
.. module:: utils.http_validator.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: HTTP request validation.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import uuid
from errata.utils import logger
from errata.issue_manager.constants import __JSON_SCHEMA_PATHS__
from errata.issue_manager.utils import *
from errata.issue_manager.custom_exceptions import *
import json, jsonschema
import cerberus


# Invalid request HTTP response code.
_HTTP_RESPONSE_BAD_REQUEST = 400


class _RequestBodyValidator(object):
    """An HTTP request body validator.

    """
    def __init__(self, request, schema):
        """Instance initializer.

        """
        self.request = request
        self.schema = schema
        self.errors = None


    def validate(self):
        """Validates the request body.

        """
        # with open(__JSON_SCHEMA_PATHS__['create']) as f:
        #     schema = json.load(f)
        schema = self.schema
        # Validate issue attributes against JSON issue schema
        request = json.loads(self.request.body)
        try:
            jsonschema.validate(request, schema)
        except jsonschema.exceptions.ValidationError as e:
            print(repr(e))
            self.errors = UnreachableURLs
            raise InvalidJSONSchema
        # Test landing page and materials URLs
        urls = filter(None, traverse(map(request.get, ['url', 'materials'])))
        if not all(map(test_url, urls)):
            self.errors = UnreachableURLs
            raise UnreachableURLs
        # Validate the datasets list against the dataset id pattern
        if not all(map(test_pattern, request['datasets'])):
            raise InvalidDatasetIDs
        if 'uid' in request.keys():
            logging.info('VALID ISSUE :: {}'.format(request['uid']))
        else:
            logging.info('VALID ISSUE :: {}'.format(request['id']))

        return []


class _RequestQueryParamsValidator(cerberus.Validator):
    """An HTTP request query params validator that extends the cerberus library.

    """
    def __init__(self, schema):
        """Instance initializer.

        """
        super(_RequestQueryParamsValidator, self).__init__(schema)


    def _validate_type_uuid(self, field, value):
        """Enables validation for `uuid` schema attribute.

        """
        try:
            uuid.UUID(value)
        except ValueError:
            self._error(field, cerberus.errors.ERROR_BAD_TYPE.format('uuid'))


    def _validate_allowed_case_insensitive(self, allowed_values, field, value):
        """Enables validation for `allowed_case_insensitive` schema attribute.

        """
        value = [i.lower() for i in value]
        allowed = [i.lower() for i in allowed_values]
        super(_RequestQueryParamsValidator, self)._validate_allowed(allowed, field, value)


def _log(handler, error):
    """Logs a security related response.

    """
    msg = "[{0}]: --> security --> {1} --> {2}"
    msg = msg.format(id(handler), handler, error)
    logger.log_web_security(msg)


def is_request_valid(handler, schema, options={}):
    """Returns a flag indicating whether an HTTP request is considered to be valid.

    """
    # Validate request.
    if isinstance(schema, dict):
        validator = _RequestBodyValidator(handler.request, schema)
        validator.validate()
    else:
        validator = _RequestQueryParamsValidator(schema)
        validator.allow_unknown = options.get('allow_unknown', False)
        validator.validate(handler.request.query_arguments)

    # HTTP 400 if request is invalid.
    if validator.errors:
        _log(handler, "Invalid request :: {}".format(validator.errors))
        handler.clear()
        handler.send_error(_HTTP_RESPONSE_BAD_REQUEST)
    return validator.errors is None
