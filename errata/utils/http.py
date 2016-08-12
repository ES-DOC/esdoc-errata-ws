# -*- coding: utf-8 -*-
"""
.. module:: utils.http.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: HTTP request handler utility functions.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import tornado

from errata.utils import logger
from errata.utils import http_validator
from errata.utils.http_invoker import execute as process_request



# HTTP CORS header.
HTTP_HEADER_Access_Control_Allow_Origin = "Access-Control-Allow-Origin"

# Supported content types.
_CONTENT_TYPE_JSON = [
    "application/json",
    "application/json; charset=UTF-8"
]

# HTTP header - Content-Type.
_HTTP_HEADER_CONTENT_TYPE = "Content-Type"


class HTTPRequestHandler(tornado.web.RequestHandler):
    """A web service request handler.

    """
    @property
    def _can_return_debug_info(self):
        """Gets flag indicating whether the application can retrun debug information.

        """
        return self.application.settings.get('debug', False)


    def invoke(
        self,
        taskset,
        error_taskset=[]
        ):
        """Invokes handler tasks.

        """
        # Log all requests.
        msg = "[{0}]: executing --> {1}"
        msg = msg.format(id(self), self)
        logger.log_web(msg)

        # Process request.
        process_request(self, taskset, error_taskset)


    def validate_request_json_headers(self):
        """Validates request JSON headers.

        """
        if _HTTP_HEADER_CONTENT_TYPE not in self.request.headers:
            raise ValueError("Content-Type HTTP header is required")

        header = self.request.headers[_HTTP_HEADER_CONTENT_TYPE]
        if not header in _CONTENT_TYPE_JSON:
            raise ValueError("Content-Type is unsupported")


    def validate_request_params(self, schema, allow_unknown=False):
        """Validates request query parameters against a cerberus schema.

        :param str schema: Cerberus schema to be used to validate request query parameters.
        :param bool allow_unknown: Flag indicating whether unknown url parameters are allowed.

        :raises: exceptions.SecurityError

        """
        http_validator.validate_request_params(self, schema, allow_unknown)


    def validate_request_body(self, schema):
        """Validates request body against a JSON schema.

        :param str schema: JSON schema to be used to validate request body.

        :raises: exceptions.SecurityError, exceptions.InvalidJSONSchemaError

        """
        http_validator.validate_request_body(self, schema)
