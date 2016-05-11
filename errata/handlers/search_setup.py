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



class SearchSetupRequestHandler(HTTPRequestHandler):
    """Search issue request handler.

    """
    def get(self):
        """HTTP GET handler.

        """
        def _set_output():
            """Sets response to be returned to client.

            """
            self.output_encoding = 'json'
            self.output = {
                'workflow': constants.WORKFLOW,
                'severity': constants.SEVERITY,
                'status': constants.STATUS
            }


        # Invoke tasks.
        self.invoke(None, _set_output)
