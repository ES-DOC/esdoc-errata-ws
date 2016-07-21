# -*- coding: utf-8 -*-

"""
.. module:: handlers.hs_handler.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - handle service search endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
from errata.issue_manager.manager import *
from errata.issue_manager.constants import __JSON_SCHEMA_PATHS__
from errata.utils.http import HTTPRequestHandler
import json
import time

with open(__JSON_SCHEMA_PATHS__['update']) as f:
    schema = f.read()


class UpdateRequestHandler(HTTPRequestHandler):
    """issue handler.

    """
    def __init__(self, application, request, **kwargs):
        """Instance constructor.

        """
        super(UpdateRequestHandler, self).__init__(application, request, **kwargs)
        self.json_body = None
        self.date_updated = None

    def post(self):
        """
        HTTP POST HANDLER
        """
        def _decode_request():
            self.json_body = json.loads(self.request.body)

        def _invoke_issue_handler():
            issue = self.json_body
            self.message, self.status = update(issue)
            if self.status == 0:
                self.date_updated = time.strftime('%Y/%m/%d %I:%M:%S %p')

        def _set_output():
            self.output = {
                'message': self.message,
                'status': self.status,
                'date_updated': self.date_updated,
            }

        self.invoke(schema, [_decode_request, _invoke_issue_handler, _set_output])
