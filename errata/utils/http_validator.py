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
from errata.schemas import get_schema


# Invalid request HTTP response code.
_HTTP_RESPONSE_BAD_REQUEST = 400


def _throw(handler, error):
    """Throws a validation error.

    """
    # Send 400 to client.
    handler.clear()
    handler.send_error(_HTTP_RESPONSE_BAD_REQUEST)

    # Bubble up error.
    raise error


def validate_request_params1(handler):
    """Validates request parameters against a JSON schema.

    :param HttpHandler handler: Request handler being processed.

    :raises: exceptions.SecurityError, exceptions.InvalidJSONSchemaError

    """
    # Map request to schema.
    schema = get_schema('params', handler.request.path)

    # Null case.
    if schema is None:
        if handler.request.query_arguments:
            _throw(handler, exceptions.SecurityError("Unexpected request url parameters."))
        return

    # Validate request parameters against schema.
    try:
        jsonschema.validate(handler.request.query_arguments, schema)
    except jsonschema.exceptions.ValidationError as json_errors:
        _throw(handler, exceptions.InvalidJSONSchemaError(json_errors))


def validate_request_body(handler):
    """Validates request body against a JSON schema.

    :param HttpHandler handler: Request handler being processed.

    :raises: exceptions.SecurityError, exceptions.InvalidJSONSchemaError

    """
    # Map request to schema.
    schema = get_schema('body', handler.request.path)

    # Null case.
    if schema is None:
        if handler.request.body:
            _throw(handler, exceptions.SecurityError("Unexpected request body."))
        return

    # Decode request data.
    data = json.loads(handler.request.body)

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
