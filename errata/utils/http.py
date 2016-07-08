# -*- coding: utf-8 -*-
"""
.. module:: utils.http.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - http utility functions.

.. moduleauthor:: Atef Benasser <abenasser@ipsl.jussieu.fr>


"""
import json

import tornado

from errata.utils import logger
from errata.utils.convert import to_namedtuple
from errata.utils.http_invoker import execute as process_request
from errata.utils.http_validator import is_request_valid



# HTTP CORS header.
HTTP_HEADER_Access_Control_Allow_Origin = "Access-Control-Allow-Origin"


class HTTPRequestHandler(tornado.web.RequestHandler):
    """A web service request handler.

    """
    def decode_json_body(self, as_namedtuple=True):
        """Decodes request body JSON string.

        :param tornado.web.RequestHandler handler: A web request handler.

        :returns: Decoded json data.
        :rtype: namedtuple | None

        """
        if not self.request.body:
            return None

        body = json.loads(self.request.body)

        return to_namedtuple(body) if as_namedtuple else body


    def invoke(
        self,
        schema,
        taskset,
        error_taskset=[]
        ):
        """Invokes handler tasks.

        """
        # Log all requests.
        msg = "[{0}]: executing --> {1}"
        msg = msg.format(id(self), self)
        logger.log_web(msg)

        # Validate & process request.
        if is_request_valid(self, schema):
            process_request(self, taskset, error_taskset)
