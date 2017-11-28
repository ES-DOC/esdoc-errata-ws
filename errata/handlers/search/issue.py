# -*- coding: utf-8 -*-

"""
.. module:: handlers.search.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - search issues endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import collections

import tornado

from errata import db
from errata.utils import constants
from errata.utils.http import process_request



# Query parameters.
_PARAM_CRITERIA = 'criteria'


class IssueSearchRequestHandler(tornado.web.RequestHandler):
    """Search issue request handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(constants.HTTP_HEADER_Access_Control_Allow_Origin, "*")


    def get(self):
        """HTTP GET handler.

        """
        def _set_criteria():
            """Sets search criteria.

            """
            self.criteria = self.get_argument(_PARAM_CRITERIA).split(',')


        def _set_data():
            """Pulls data from db.

            """
            with db.session.create():
                self.issues = db.dao.get_issues(self.criteria)
                self.total = db.utils.get_count(db.models.Issue)


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                'count': len(self.issues),
                'results': self.issues,
                'total': self.total,
            }


        # Process request.
        process_request(self, [
            _set_criteria,
            _set_data,
            _set_output
            ])
