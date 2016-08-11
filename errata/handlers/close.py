# -*- coding: utf-8 -*-

"""
.. module:: handlers.hs_handler.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - handle service search endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import json

from errata.issue_manager.manager import *
from errata.issue_manager.constants import JSON_SCHEMAS
from errata.utils.http import HTTPRequestHandler



class CloseRequestHandler(HTTPRequestHandler):
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
            self.message, self.status, self.date_closed = close(self.json_body['id'])


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                "message": self.message,
                "status": self.status,
                "date_closed": self.date_closed
            }


        # Invoke tasks.
        self.invoke(JSON_SCHEMAS['close'], [
            _decode_request,
            _invoke_issue_handler,
            _set_output
            ])

