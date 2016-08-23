# -*- coding: utf-8 -*-

"""
.. module:: handlers.resolve.issue_from_model.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - resolve issues from model endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import tornado

from errata import db
from errata.utils import constants
from errata.utils.http import process_request



# Query parameter names.
_PARAM_MODEL_ID = 'model'



class ResolveIssueFromModelRequestHandler(tornado.web.RequestHandler):
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
            with db.session.create():
                self.issues = db.dao.get_model_issues(self.get_argument(_PARAM_MODEL_ID))


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                'count': len(self.issues),
                'issueIdentifiers': self.issues,
                'modelID': self.get_argument(_PARAM_MODEL_ID)
            }


        # Process request.
        process_request(self, [
            _set_data,
            _set_output
            ])
