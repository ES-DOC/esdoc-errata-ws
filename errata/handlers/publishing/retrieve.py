# -*- coding: utf-8 -*-

"""
.. module:: handlers.retrieve.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - retrieve issue endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
from errata import db
from errata.utils import convertor
from errata.utils.http import HTTPRequestHandler
from errata.utils.http import HTTP_HEADER_Access_Control_Allow_Origin



# Query parameter names.
_PARAM_UID = 'uid'

# Query parameter validation schema.
_REQUEST_PARAMS_SCHEMA = {
    _PARAM_UID: {
        'required': True,
        'type': 'list', 'items': [{'type': 'uuid'}]
    }
}


class RetrieveIssueRequestHandler(HTTPRequestHandler):
    """Retrieve issue request handler.

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
            self.validate_request_params(_REQUEST_PARAMS_SCHEMA)
            self.validate_request_body(None)


        def _decode_request():
            """Decodes request.

            """
            self.uid = self.get_argument(_PARAM_UID)


        def _set_data():
            """Pulls data from db.

            """
            with db.session.create():
                self.issue = db.dao.get_issue(self.uid)
                self.datasets = db.dao.get_issue_datasets(self.issue.uid)


        def _set_output():
            """Sets response to be returned to client.

            """
            # Encode issue as a simple dictionary.
            obj = convertor.to_dict(self.issue)

            # Remove db injected fields.
            del obj['id']
            del obj['row_create_date']
            del obj['row_update_date']

            # Set array fields.
            obj['datasets'] = self.datasets
            obj['materials'] = sorted(self.issue.materials.split(","))
            obj['models'] = []      # TODO refactor when implemented.

            self.output = {
                'issue': obj
            }


        # Invoke tasks.
        self.invoke([
            _validate_request,
            _decode_request,
            _set_data,
            _set_output
            ])
