# -*- coding: utf-8 -*-

"""
.. module:: handlers.search_setup.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - search setup endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import tornado

from errata.utils import constants
from errata.utils.http import process_request



class IssueSearchSetupRequestHandler(tornado.web.RequestHandler):
    """Search issue request handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(constants.HTTP_HEADER_Access_Control_Allow_Origin, "*")


    def get(self):
        """HTTP GET handler.

        """
        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                'institute': constants.INSTITUTE,
                'project': constants.PROJECT,
                'severity': constants.SEVERITY,
                'status': constants.STATUS
            }


        # Process request.
        process_request(self, _set_output)
