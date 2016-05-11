# -*- coding: utf-8 -*-

"""
.. module:: handlers.hs_handler.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - handle service search endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
from errata.utils.http import HTTPRequestHandler
from errata.handle_service.harvest import harvest_errata_information
from errata import db

# Query parameter names.
_PARAM_UID = 'handle'



class HandleServiceRequestHandler(HTTPRequestHandler):
    """Retrieve issue request handler.

    """
    def __init__(self, application, request, **kwargs):
        """Instance constructor.

        """
        super(HandleServiceRequestHandler, self).__init__(application, request, **kwargs)

        self.handle_string = None
        self.list_of_uids = None
        self.issues = None

    def get(self):
        """HTTP GET handler.

        """
        def _decode_request():
            """Decodes request.

            """
            self.handle_string = self.get_argument(_PARAM_UID)

        def _set_data():
            """Pulls data from db.

            """
            self.list_of_uids = harvest_errata_information(self.handle_string)
            with db.session.create():
                self.issues = db.dao.get_issues_by_uids(self.list_of_uids)

        def _set_output():
            """Sets response to be returned to client.

            """
            self.output_encoding = 'json'
            self.output = {
                'issues': self.issues
            }

        # Invoke tasks.
        # TODO input request validation.
        self.invoke([], [
            _decode_request,
            _set_data,
            _set_output
            ])
