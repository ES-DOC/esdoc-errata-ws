# -*- coding: utf-8 -*-

"""
.. module:: handlers.close.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - close issue endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import datetime as dt

from errata import db
from errata.utils import constants
from errata.utils.http import HTTPRequestHandler



# Query parameter names.
_PARAM_UID = 'uid'


class CloseIssueRequestHandler(HTTPRequestHandler):
    """issue handler.

    """
    def post(self):
        """HTTP POST handler.

        """
        def _validate_issue_exists():
            """Validates that issue exists within dB.

            """
            with db.session.create():
                self.issue = db.dao.get_issue(self.get_argument(_PARAM_UID))
            if self.issue is None:
                raise ValueError("Issue does not exist")


        def _validate_issue_status():
            """Validates that issue state allows it to be closed.

            """
            if self.issue.workflow in [
                constants.WORKFLOW_WONT_FIX,
                constants.WORKFLOW_RESOLVED
                ]:
                raise ValueError("Issue state is not closeable")


        def _close_issue():
            """Closes issue.

            """
            self.issue.state = constants.STATE_CLOSED
            self.issue.date_closed = dt.datetime.utcnow()
            with db.session.create():
                db.session.update(self.issue)


        # Invoke tasks.
        self.invoke([
            _validate_issue_exists,
            _validate_issue_status,
            _close_issue
            ])
