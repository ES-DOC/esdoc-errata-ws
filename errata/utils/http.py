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
from errata.utils import http_invoker
from errata.utils import http_validator



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


    def invoke(self, taskset, error_taskset=None):
        """Invokes handler tasks.

        :param list taskset: Set of request processing tasks.
        :param list error_taskset: Set of error processing tasks.

        """
        # Log all requests.
        msg = "[{0}]: executing --> {1}"
        msg = msg.format(id(self), self)
        logger.log_web(msg)

        # Process request.
        http_invoker.execute(self, taskset, error_taskset or [])


    def throw(self, error):
        """Throws a trapped processing error.

        """
        # Send 400 to client.
        self.clear()
        self.send_error(400)

        # Bubble up error.
        raise error
