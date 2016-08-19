# -*- coding: utf-8 -*-

"""
.. module:: handlers.resolve.issue_from_dataset.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - resolve issues from dataset endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from errata import db
from errata.utils.http import HTTPRequestHandler
from errata.utils.http import HTTP_HEADER_Access_Control_Allow_Origin



# Query parameter names.
_PARAM_DATASET_ID = 'dataset'


class ResolveIssueFromDatasetRequestHandler(HTTPRequestHandler):
    """Search issue request handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(HTTP_HEADER_Access_Control_Allow_Origin, "*")


    def get(self):
        """HTTP GET handler.

        """
        def _set_data():
            """Pulls data from db.

            """
            with db.session.create():
                self.issues = db.dao.get_dataset_issues(self.get_argument(_PARAM_DATASET_ID))


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                'count': len(self.issues),
                'issueIdentifiers': self.issues,
                'datasetID': self.get_argument(_PARAM_DATASET_ID)
            }


        # Invoke tasks.
        self.invoke([
            _set_data,
            _set_output
            ])
