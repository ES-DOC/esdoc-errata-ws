# -*- coding: utf-8 -*-
"""
.. module:: utils.http_validator.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: HTTP request validation.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import json
import uuid

import cerberus
import jsonschema

from errata.utils import exceptions
from errata.utils import logger



# Invalid request HTTP response code.
_HTTP_RESPONSE_BAD_REQUEST = 400


def _throw(handler, error):
    """Throws a validation error.

    """
    # Log.
    msg = "[{0}]: --> security --> {1} --> Invalid request :: {2}"
    msg = msg.format(id(handler), handler, error)
    logger.log_web_security(msg)

    # Send 400 to client.
    handler.clear()
    handler.send_error(_HTTP_RESPONSE_BAD_REQUEST)

    # Bubble up error.
    raise error


def validate_request_body(handler, schema):
    """Validates request body against a JSON schema.

    :param HttpHandler handler: Request handler being processed.
    :param str schema: JSON schema to be used to validate request body.

    :raises: exceptions.SecurityError, exceptions.InvalidJSONSchemaError

    """
    # Null case.
    if schema is None:
        if handler.request.body:
            _throw(handler, exceptions.SecurityError("Unexpected request body."))
        return

    # Decode request data & schema.
    data = json.loads(handler.request.body)
    schema = json.loads(schema)

    # Validate request data against schema.
    try:
        jsonschema.validate(data, schema)
    except jsonschema.exceptions.ValidationError as json_errors:
        _throw(handler, exceptions.InvalidJSONSchemaError(json_errors))

    # As data is valid append to request.
    handler.request.data = data


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


def validate_request_params(handler, schema, allow_unknown=False):
    """Validates request query parameters against a cerberus schema.

    :param HttpHandler handler: Request handler being processed.
    :param str schema: Cerberus schema to be used to validate request query parameters.
    :param bool allow_unknown: Flag indicating whether unknown url parameters are allowed.

    :raises: exceptions.SecurityError

    """
    # Null case.
    if schema is None:
        if handler.request.query_arguments:
            _throw(handler, exceptions.SecurityError("Unexpected request url parameters."))
        return

    validator = _RequestQueryParamsValidator(schema)
    validator.allow_unknown = allow_unknown
    validator.validate(handler.request.query_arguments)

    print validator.errors
