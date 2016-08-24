# -*- coding: utf-8 -*-

"""
.. module:: handlers.search.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - search issues endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import tornado

from errata import db
from errata.utils import constants
from errata.utils.http import process_request



# Query parameter names.
_PARAM_INSTITUTE = 'institute'
_PARAM_PROJECT = 'project'
_PARAM_SEVERITY = 'severity'
_PARAM_TIMESTAMP = 'timestamp'
_PARAM_WORKFLOW = 'workflow'


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
            for param in {
                _PARAM_INSTITUTE,
                _PARAM_PROJECT,
                _PARAM_SEVERITY,
                _PARAM_WORKFLOW,
            }:
                if self.get_argument(param) != "*":
                    setattr(self, param, self.get_argument(param).lower())
                else:
                    setattr(self, param, None)


        def _set_data():
            """Pulls data from db.

            """
            with db.session.create():
                self.issues = db.dao.get_issues(
                    institute=self.institute,
                    project=self.project,
                    workflow=self.workflow,
                    severity=self.severity
                    )
                self.total = db.utils.get_count(db.models.Issue)


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                'count': len(self.issues),
                'results': self.issues,
                'timestamp': self.get_argument(_PARAM_TIMESTAMP),
                'total': self.total,
            }


        # Process request.
        process_request(self, [
            _set_criteria,
            _set_data,
            _set_output
            ])
