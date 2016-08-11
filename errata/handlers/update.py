# -*- coding: utf-8 -*-

"""
.. module:: handlers.hs_handler.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - handle service search endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import json

from errata.issue_manager.constants import JSON_SCHEMAS
from errata.issue_manager.manager import *
from errata.utils.http import HTTPRequestHandler



class UpdateRequestHandler(HTTPRequestHandler):
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
            self.message, self.status, update_time = update(self.json_body)
            if self.status == 0:
                self.date_updated = update_time
            else:
                self.date_updated = None


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                'date_updated': self.date_updated,
                'message': self.message,
                'status': self.status
            }


        # Invoke tasks.
        self.invoke(JSON_SCHEMAS['update'], [
            _decode_request,
            _invoke_issue_handler,
            _set_output
            ])
