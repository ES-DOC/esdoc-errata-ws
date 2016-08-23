# -*- coding: utf-8 -*-

"""
.. module:: handlers.close.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - close issue endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import datetime as dt

import tornado

from errata import db
from errata.utils import constants
from errata.utils import exceptions
from errata.utils.http import process_request



# Query parameter names.
_PARAM_UID = 'uid'


class CloseIssueRequestHandler(tornado.web.RequestHandler):
    """issue handler.

    """
    def post(self):
        """HTTP POST handler.

        """
        def _validate_issue_exists():
            """Validates that issue exists within dB.

            """
            global issue

            issue = db.dao.get_issue(self.get_argument(_PARAM_UID))
            if issue is None:
                raise exceptions.UnknownIssueError(self.get_argument(_PARAM_UID))


        def _validate_issue_status():
            """Validates that issue state allows it to be closed.

            """
            global issue

            if issue.workflow in [
                constants.WORKFLOW_WONT_FIX,
                constants.WORKFLOW_RESOLVED
                ]:
                raise exceptions.InvalidIssueStatusError()


        def _close_issue():
            """Closes issue.

            """
            global issue

            issue.state = constants.STATE_CLOSED
            issue.date_closed = dt.datetime.utcnow()


        # Initialize shared processing variables.
        issue = None

        # Process request.
        with db.session.create(commitable=True):
            process_request(self, [
                _validate_issue_exists,
                _validate_issue_status,
                _close_issue
                ])
