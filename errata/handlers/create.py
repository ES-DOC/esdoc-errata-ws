# -*- coding: utf-8 -*-

"""
.. module:: handlers.hs_handler.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - issue creation endpoint.

.. module author:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import json

from errata.issue_manager.constants import JSON_SCHEMAS
from errata.issue_manager.manager import create
from errata.utils.http import HTTPRequestHandler



class CreateRequestHandler(HTTPRequestHandler):
    """issue handler.

    """
    def post(self):
        """HTTP POST handler.

        """
        def _decode_request():
            """Decodes request.

            """
            self.json_body = json.loads(self.request.body)


        def _invoke_issue_handler():
            """Invokes issue handler utility function.

            """
            self.message, self.status, creation_time = create(self.json_body)
            if self.status == 0:
                self.date_created = creation_time
                self.date_updated = self.date_created
                self.workflow = self.json_body['workflow']
            else:
                self.date_created = None
                self.date_updated = None
                self.workflow = None


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                "date_created": self.date_created,
                "date_updated": self.date_updated,
                "message": self.message,
                "status": self.status,
                "workflow": self.workflow
            }


        # Invoke tasks.
        self.invoke(JSON_SCHEMAS['create'], [
            _decode_request,
            _invoke_issue_handler,
            _set_output
            ])

