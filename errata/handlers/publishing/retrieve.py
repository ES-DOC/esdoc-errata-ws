# -*- coding: utf-8 -*-

"""
.. module:: handlers.retrieve.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - retrieve issue endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import tornado

from errata import db
from errata.utils import constants
from errata.utils.http import process_request



# Query parameter names.
_PARAM_UID = 'uid'


class RetrieveIssueRequestHandler(tornado.web.RequestHandler):
    """Retrieve issue request handler.

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
            with db.session.create():
                self.issue = db.dao.get_issue(self.get_argument(_PARAM_UID))
                self.resources = db.dao.get_resources(issue_uid=self.get_argument(_PARAM_UID))


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                'issue': self.issue.to_dict(self.resources)
            }


        # Process request.
        process_request(self, [
            _set_data,
            _set_output
            ])
