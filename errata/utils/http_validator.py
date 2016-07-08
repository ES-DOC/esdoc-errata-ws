# -*- coding: utf-8 -*-
"""
.. module:: utils.http_validator.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - http validation functions.

.. moduleauthor:: Atef Benasser <abenasser@ipsl.jussieu.fr>


"""
import uuid

import cerberus

from errata.utils import logger



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


    def validate(self):
        """Validates the request body.

        """
        # TODO implement using jsonschema ?
        return []


class _RequestQueryParamsValidator(cerberus.Validator):
    """An HTTP request query params validator that extends the cerberus library.

    """
    def __init__(self, request, schema):
        """Instance initializer.

        """
        super(_RequestQueryParamsValidator, self).__init__(schema)

        self.query_arguments = request.query_arguments


    def _validate_type_uuid(self, field, value):
        """Enables validation for `uuid` schema attribute.

        """
        try:
            uuid.UUID(value)
        except ValueError:
            self._error(field, cerberus.errors.ERROR_BAD_TYPE.format('uuid'))


    def validate(self):
        """Validates request parameters against schema.

        """
        return super(_RequestQueryParamsValidator, self).validate(self.query_arguments)


def _log(handler, error):
    """Logs a security related response.

    """
    msg = "[{0}]: --> security --> {1} --> {2}"
    msg = msg.format(id(handler), handler, error)
    logger.log_web_security(msg)


def is_request_valid(handler, schema):
    """Returns a flag indicating whether an HTTP request is considered to be valid.

    """
    # Set validator.
    if isinstance(schema, str):
        validator = _RequestBodyValidator
    else:
        validator = _RequestQueryParamsValidator
    validator = validator(handler.request, schema)

    # Validate request.
    validator.validate()

    # HTTP 400 if request is invalid.
    if validator.errors:
        _log(handler, "Invalid request :: {}".format(validator.errors))
        handler.clear()
        handler.send_error(_HTTP_RESPONSE_BAD_REQUEST)

    return len(validator.errors) == 0
