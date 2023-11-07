import tornado
from errata_ws import db
from errata_ws import notifications
from errata_ws.utils import config
from errata_ws.utils import constants
from errata_ws.utils import exceptions
from errata_ws.utils import http_security
from errata_ws.utils.http import process_request



class ModerateErrataRequestHandler(tornado.web.RequestHandler):
    """Moderation errata handler.

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
            self.issue = db.dao.get_issue(self.request.data[constants.JF_UID])
            if self.issue is None:
                raise exceptions.UnknownIssueError(self.request.data[constants.JF_UID])


        def _validate_user_access():
            if config.apply_security_policy:
                http_security.authorize_moderation(self.user_id, self.issue.project, self.issue.institute)


        def _update_moderation_status():
            self.issue.moderation_status = self.request.data[constants.JF_MODERATION_STATUS]


        def _notify():
            """Notifies proposer & moderation team.

            """
            if self.issue.moderation_status == constants.ISSUE_MODERATION_ACCEPTED:
                notifications.dispatch_on_accepted(
                    self.request.protocol,
                    self.request.host,
                    self.issue.created_by,
                    self.issue.uid
                )
            elif self.issue.moderation_status == constants.ISSUE_MODERATION_REJECTED:
                notifications.dispatch_on_rejected(
                    self.request.protocol,
                    self.request.host,
                    self.issue.created_by,
                    self.issue.uid
                )

    
        with db.session.create(commitable=True):
            process_request(self, [
                _validate_issue_exists,
                _validate_user_access,
                _update_moderation_status,
                _notify
                ])
