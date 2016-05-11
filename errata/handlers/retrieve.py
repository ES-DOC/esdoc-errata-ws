# -*- coding: utf-8 -*-

"""
.. module:: handlers.retrieve.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - retrieve issue endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from errata import db
from errata.utils.http import HTTPRequestHandler



# Query parameter names.
_PARAM_UID = 'uid'

# URL query parameter validation schema.
_REQUEST_VALIDATION_SCHEMA = {
    _PARAM_UID: {
        'required': True,
        'type': 'list', 'items': [{'type': 'string'}]
    }
}


class RetrieveRequestHandler(HTTPRequestHandler):
    """Retrieve issue request handler.

    """
    def __init__(self, application, request, **kwargs):
        """Instance constructor.

        """
        super(RetrieveRequestHandler, self).__init__(application, request, **kwargs)

        self.uid = None
        self.issue = None


    def get(self):
        """HTTP GET handler.

        """
        def _decode_request():
            """Decodes request.

            """
            self.uid = self.get_argument(_PARAM_UID)


        def _set_data():
            """Pulls data from db.

            """
            with db.session.create():
                self.issue = db.dao.get_issue(self.uid)


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output_encoding = 'json'
            self.output = {
                'issue': self.issue
            }


        # Invoke tasks.
        self.invoke(_REQUEST_VALIDATION_SCHEMA, [
            _decode_request,
            _set_data,
            _set_output
            ])
