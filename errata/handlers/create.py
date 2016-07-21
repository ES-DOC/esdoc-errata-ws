# -*- coding: utf-8 -*-

"""
.. module:: handlers.hs_handler.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - issue creation endpoint.

.. module author:: Atef Bennasser <abenasser@ipsl.jussieu.fr>
"""

from errata.issue_manager.manager import create
from errata.issue_manager.constants import __JSON_SCHEMA_PATHS__
from errata.utils.http import HTTPRequestHandler
import json

with open(__JSON_SCHEMA_PATHS__['create']) as f:
    schema = f.read()

class CreateRequestHandler(HTTPRequestHandler):
    """issue handler.

    """
    def __init__(self, application, request, **kwargs):
        """Instance constructor.

        """
        super(CreateRequestHandler, self).__init__(application, request, **kwargs)
        self.json_body = None

    def post(self):
        """
        HTTP POST HANDLER
        """
        def _decode_request():
            self.json_body = json.loads(self.request.body)

        def _invoke_issue_handler():
            issue = self.json_body
            self.message, self.status = create(issue)

        def _set_output():
            self.output = {
                "message": self.message,
                "status": self.status
            }
        self.invoke(schema, [_decode_request, _invoke_issue_handler, _set_output])
