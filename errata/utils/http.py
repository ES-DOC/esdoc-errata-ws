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



# HTTP CORS header.
HTTP_HEADER_Access_Control_Allow_Origin = "Access-Control-Allow-Origin"


class HTTPRequestHandler(tornado.web.RequestHandler):
    """A web service request handler.

    """
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
