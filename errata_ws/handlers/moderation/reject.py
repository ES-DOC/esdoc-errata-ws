import tornado

from errata_ws import db
from errata_ws.utils import config
from errata_ws.utils import constants
from errata_ws.utils import exceptions
from errata_ws.utils import http_security
from errata_ws.utils.http import process_request


# Query parameter names.
_PARAM_UID = 'uid'


class RejectIssueRequestHandler(tornado.web.RequestHandler):
    """Moderation reject issue handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        http_security.set_headers(self, True)


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
            """Validates user's access rights.

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
