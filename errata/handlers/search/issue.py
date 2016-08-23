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
_PARAM_STATE = 'state'
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
            global institute, project, severity, state, workflow

            if self.get_argument(_PARAM_INSTITUTE) != "*":
                institute = self.get_argument(_PARAM_INSTITUTE).lower()
            if self.get_argument(_PARAM_PROJECT) != "*":
                project = self.get_argument(_PARAM_PROJECT).lower()
            if self.get_argument(_PARAM_SEVERITY) != "*":
                severity = self.get_argument(_PARAM_SEVERITY).lower()
            if self.get_argument(_PARAM_STATE) != "*":
                state = self.get_argument(_PARAM_STATE).lower()
            if self.get_argument(_PARAM_WORKFLOW) != "*":
                workflow = self.get_argument(_PARAM_WORKFLOW).lower()


        def _set_data():
            """Pulls data from db.

            """
            global institute, issues, project, severity, state, total, workflow

            with db.session.create():
                issues = db.dao.get_issues(
                    institute=institute,
                    project=project,
                    state=state,
                    workflow=workflow,
                    severity=severity
                    )
                total = db.utils.get_count(db.models.Issue)


        def _set_output():
            """Sets response to be returned to client.

            """
            global issues, total

            self.output = {
                'count': len(issues),
                'results': issues,
                'timestamp': self.get_argument(_PARAM_TIMESTAMP),
                'total': total,
            }


        # Initialize shared processing variables.
        institute = issues = project = severity = state = total = workflow = None

        # Process request.
        process_request(self, [
            _set_criteria,
            _set_data,
            _set_output
            ])
