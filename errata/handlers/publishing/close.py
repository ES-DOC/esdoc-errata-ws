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
_PARAM_STATUS = 'status'

# ESDOC GitHub team: errata-publication.
_ESDOC_GH_TEAM_ERRATA_PUBLICATION = 'errata-publication'



class CloseIssueRequestHandler(tornado.web.RequestHandler):
    """issue handler.

    """
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
            # Super & insitutional users have access.
            for team in sorted(self.user_teams):
                if team == constants.ERRATA_GH_TEAM:
                    return
                if team.split("-")[-1] == self.issue.institution_id:
                    return
            # User has no access rights to this particular issue.
            raise exceptions.AuthorizationError()



        def _validate_issue_status():
            """Validates that issue status allows it to be closed.

            """
            if self.issue.status in [
                constants.STATUS_ON_HOLD,
                constants.STATUS_NEW
                ]:
                raise exceptions.InvalidIssueStatusError()


        def _close_issue():
            """Closes issue.

            """
            # TODO: get date_closed from closedAt field
            self.issue.date_closed = dt.datetime.utcnow()
            self.issue.closed_by = self.user_name
            self.issue.status = self.get_argument(_PARAM_STATUS)


        # Process request.
        with db.session.create(commitable=True):
            process_request(self, [
                _validate_issue_exists,
                _validate_user_access,
                _validate_issue_status,
                _close_issue
                ])
