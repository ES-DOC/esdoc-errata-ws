# -*- coding: utf-8 -*-

"""
.. module:: handlers.search.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - search issues endpoint.

.. moduleauthor:: Atef Bennasser <abennasser@ipsl.jussieu.fr>


"""
from errata import constants
from errata import db
from errata.utils.http import HTTPRequestHandler



class SearchSetupRequestHandler(HTTPRequestHandler):
    """Search issue request handler.

    """
    def get(self):
        """HTTP GET handler.

        """
        def _set_data():
            """Pulls data from db.

            """
            with db.session.create():
                # TODO - pull required data from db
                pass


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output_encoding = 'json'
            self.output = {
                'workflow_state': constants.WORKFLOW_,
                'severities': constants.ISSUE_SEVERITY
            }


        # Invoke tasks.
        self.invoke([], [
            _set_data,
            _set_output
            ])
