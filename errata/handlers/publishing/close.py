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
from errata.utils import config
from errata.utils import constants
from errata.utils import exceptions
from errata.utils.http import process_request
from errata.utils.http_security import authorize
from errata.utils.publisher import close_issue


# Query parameter names.
_PARAM_UID = 'uid'
_PARAM_STATUS = 'status'


class CloseIssueRequestHandler(tornado.web.RequestHandler):
    """issue handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(constants.HTTP_HEADER_Access_Control_Allow_Origin, "*")
        self.set_header("Access-Control-Allow-Headers", "content-type, Authorization")
        self.set_header('Access-Control-Allow-Methods', 'POST')
        self.set_header('Access-Control-Allow-Credentials', True)
        self.set_header('X-XSRFToken', self.xsrf_token)

    def options(self):
        self.set_status(204)
        self.set_default_headers()
        self.finish()

    def post(self):
        """HTTP POST handler.

        """

        def _validate_issue_exists():
            """Validates that issue exists within dB.

            """
            self.issue = db.dao.get_issue(self.get_argument(_PARAM_UID))
            if self.issue is None:
                raise exceptions.UnknownIssueError(self.get_argument(_PARAM_UID))


        def _validate_user_access():
            """Validates user's institutional access rights.

            """
            if config.apply_security_policy:
                authorize(self.user_id, self.issue.project, self.issue.institute)


        def _validate_issue_status():
            """Validates that issue status allows it to be closed.

            """
            if self.issue.status in {
                constants.STATUS_ON_HOLD,
                constants.STATUS_NEW
                }:
                raise exceptions.IssueStatusChangeError()


        def _close_issue():
            """Closes issue.

            """
            close_issue(self.issue, self.get_argument(_PARAM_STATUS), self.user_id)


        # Process request.
        with db.session.create(commitable=True):
            process_request(self, [
                _validate_issue_exists,
                _validate_user_access,
                _validate_issue_status,
                _close_issue
                ])
