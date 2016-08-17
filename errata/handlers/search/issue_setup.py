# -*- coding: utf-8 -*-

"""
.. module:: handlers.search_setup.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - search setup endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from errata.utils import constants
from errata.utils.http import HTTPRequestHandler
from errata.utils.http import HTTP_HEADER_Access_Control_Allow_Origin



class IssueSearchSetupRequestHandler(HTTPRequestHandler):
    """Search issue request handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(HTTP_HEADER_Access_Control_Allow_Origin, "*")


    def get(self):
        """HTTP GET handler.

        """
        def _validate_request():
            """Validates incoming request prior to processing.

            """
            self.validate_request_params(None)
            self.validate_request_body(None)


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                'institute': constants.INSTITUTE,
                'project': constants.PROJECT,
                'severity': constants.SEVERITY,
                'state': constants.STATE,
                'workflow': constants.WORKFLOW
            }


        # Invoke tasks.
        self.invoke([
            _validate_request,
            _set_output
            ])
