import datetime as dt

import tornado

from errata import db
from errata.utils import config
from errata.utils import exceptions
from errata.utils import http_security
from errata.utils.http import process_request


# Query parameter names.
_PARAM_UID = 'uid'


class ExtendIssueRequestHandler(tornado.web.RequestHandler):
    """Moderation extend issue handler.

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


        def _extend_issue():
            """Extends issue moderation time window.

            """
            self.issue.moderation_window += dt.timedelta(weeks=2)


        # Process request.
        with db.session.create(commitable=True):
            process_request(self, [
                _validate_issue_exists,
                _validate_user_access,
                _extend_issue
                ])
