import datetime as dt

import tornado

from errata_ws import db
from errata_ws.utils import config
from errata_ws.utils import constants
from errata_ws.utils import exceptions
from errata_ws.utils import http_security
from errata_ws.utils.http import process_request
from errata_ws.utils.http_security import authorize
from errata_ws.utils.publisher import close_issue


# Query parameter names.
_PARAM_UID = 'uid'
_PARAM_STATUS = 'status'


class CloseErrataRequestHandler(tornado.web.RequestHandler):
    """Publishing close issue handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        http_security.set_headers(self, True)


    def options(self):
        """HTTP OPTIONS handler.

        """
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
                self.user_role = authorize(
                    self.user_id,
                    self.request.data[constants.JF_PROJECT],
                    get_institute(self.request.data)
                    )
            else:
                self.user_role = None


        def _validate_issue_status():
            """Validates that issue status allows it to be closed.

            """
            if self.issue.status in {
                constants.ISSUE_STATUS_ON_HOLD,
                constants.ISSUE_STATUS_NEW
                }:
                raise exceptions.IssueStatusChangeError()


        def _close_issue():
            """Closes issue.

            """
            close_issue(self.issue, self.get_argument(_PARAM_STATUS), self.user_id, self.user_role)


        # Process request.
        with db.session.create(commitable=True):
            process_request(self, [
                _validate_issue_exists,
                _validate_user_access,
                _validate_issue_status,
                _close_issue
                ])
