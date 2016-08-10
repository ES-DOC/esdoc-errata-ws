# -*- coding: utf-8 -*-

"""
.. module:: handlers.hs_handler.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - handle service search endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""

from errata.issue_manager.manager import *
from errata.utils.http import HTTPRequestHandler
import time, json
from errata.issue_manager.constants import __JSON_SCHEMA_PATHS__

with open(__JSON_SCHEMA_PATHS__['close']) as f:
    schema = f.read()


class CloseRequestHandler(HTTPRequestHandler):
    """issue handler.

    """
    def __init__(self, application, request, **kwargs):
        """Instance constructor.

        """
        super(CloseRequestHandler, self).__init__(application, request, **kwargs)
        self.uid = None
        self.date_closed = None

    def post(self):
        """
        HTTP PUT HANDLER
        """
        def _decode_request():
            self.json_body = json.loads(self.request.body)

        def _invoke_issue_handler():
            self.message, self.status, self.date_closed = close(self.json_body['id'])

        def _set_output():
            self.output = {
                "message": self.message,
                "status": self.status,
                "date_closed": self.date_closed
            }
        self.invoke(schema, [_decode_request, _invoke_issue_handler, _set_output])

