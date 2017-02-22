# -*- coding: utf-8 -*-

"""
.. module:: handlers.resolve.issue_from_dataset.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - resolve issues from dataset endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import tornado

from errata import db
from errata.utils import constants
from errata.utils.http import process_request



# Query parameter names.
_PARAM_FACET_TYPE = 'facetType'
_PARAM_FACET_ID = 'facetID'


class ResolveIssueRequestHandler(tornado.web.RequestHandler):
    """Search issue request handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(constants.HTTP_HEADER_Access_Control_Allow_Origin, "*")


    def get(self):
        """HTTP GET handler.

        """
        def _set_data():
            """Pulls data from db.

            """
            self.issues = db.dao.get_issues_by_facet(
                self.get_argument(_PARAM_FACET_ID),
                self.get_argument(_PARAM_FACET_TYPE)
                )


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                'count': len(self.issues),
                'issueIdentifiers': self.issues,
                'facetID': self.get_argument(_PARAM_FACET_ID),
                'facetType': self.get_argument(_PARAM_FACET_TYPE)
            }


        # Process request.
        with db.session.create():
            process_request(self, [
                _set_data,
                _set_output
                ])
