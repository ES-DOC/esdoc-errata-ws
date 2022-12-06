import datetime as dt

import tornado

from errata import db
from errata.utils import config
from errata.utils import constants
from errata.utils import exceptions
from errata.utils import http_security
from errata.utils.http import process_request


# Query parameter names.
_PARAM_UID = 'uid'


class RejectIssueRequestHandler(tornado.web.RequestHandler):
    """Moderation reject issue handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(constants.HTTP_HEADER_Access_Control_Allow_Origin, "*")
        self.set_header("Access-Control-Allow-Headers", "content-type, Authorization")
        self.set_header('Access-Control-Allow-Methods', 'POST')
        self.set_header('Access-Control-Allow-Credentials', True)
        self.set_header('X-XSRFToken', self.xsrf_token)


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
                http_security.authorize_moderation(self.user_id, self.issue.project, self.issue.institute)


        def _reject_issue():
            """Rejects issue under moderation.

            """
            self.issue.moderation_status = constants.ISSUE_MODERATION_REJECTED


        # Process request.
        with db.session.create(commitable=True):
            process_request(self, [
                _validate_issue_exists,
                _validate_user_access,
                _reject_issue
                ])
