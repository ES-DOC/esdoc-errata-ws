# -*- coding: utf-8 -*-

"""
.. module:: handlers.search_setup.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - search setup endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from errata import constants
from errata.utils.http import HTTPRequestHandler
from errata.utils.http import HTTP_HEADER_Access_Control_Allow_Origin



class SearchSetupRequestHandler(HTTPRequestHandler):
    """Search issue request handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(HTTP_HEADER_Access_Control_Allow_Origin, "*")


    def get(self):
        """HTTP GET handler.

        """
        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                'institute': [
                    {
                        'key': "badc",
                        'label': "BADC"
                    },
                    {
                        'key': "dkrz",
                        'label': "DKRZ"
                    },
                    {
                        'key': "ipsl",
                        'label': "IPSL"
                    }
                ],
                'project': [
                    {
                        'key': "cmip5",
                        'label': "CMIP5"
                    },
                    {
                        'key': "cmip6",
                        'label': "CMIP6"
                    }
                ],
                'severity': constants.SEVERITY,
                'state': constants.STATE,
                'workflow': constants.WORKFLOW
            }


        # Invoke tasks.
        self.invoke([
            # ... validation tasks
            lambda: self.validate_request_params(None),
            lambda: self.validate_request_body(None),
            # ... processing tasks
            _set_output
            ])
