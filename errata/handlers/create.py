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
import time
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
        self.date_created = None
        self.date_updated = None
        self.workflow = None

    def post(self):
        """
        HTTP POST HANDLER
        """
        def _decode_request():
            self.json_body = json.loads(self.request.body)

        def _invoke_issue_handler():
            issue = self.json_body
            self.message, self.status, creation_time = create(issue)
            if self.status == 0:
                self.date_created = creation_time
                self.date_updated = self.date_created
                self.workflow = self.json_body['workflow']

        def _set_output():
            self.output = {
                "message": self.message,
                "workflow": self.workflow,
                "date_created": self.date_created,
                "date_updated": self.date_updated,
                "status": self.status,
            }
        self.invoke(schema=schema, taskset=[_decode_request, _invoke_issue_handler, _set_output])
