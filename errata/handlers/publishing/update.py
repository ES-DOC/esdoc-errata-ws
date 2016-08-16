# -*- coding: utf-8 -*-

"""
.. module:: handlers.update.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - update issue endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import difflib

from errata import db
from errata.utils import constants
from errata.utils import exceptions
from errata.utils.http import HTTPRequestHandler



class UpdateIssueRequestHandler(HTTPRequestHandler):
    """issue handler.

    """
    def post(self):
        """HTTP POST handler.

        """
        def _validate_issue_exists():
            """Validates that the issue has been previously posted to the web-service.

            """
            with db.session.create():
                self.issue = db.dao.get_issue(self.request.data['id'])
            if self.issue is None:
                raise exceptions.UnknownIssueError(self.request.data['id'])


        def _validate_issue_immutable_attributes():
            """Validates that issue attribute deemed to be immutable have not been changed.

            """
            for attr_name in constants.IMMUTABLE_ISSUE_ATTRIBUTES:
                if unicode(self.request.data[attr_name]).lower() != unicode(getattr(self.issue, attr_name)).lower():
                    raise exceptions.ImmutableIssueAttributeError(attr_name)
            print "TODO: validate date_created immutability"


        def _validate_issue_description_change_ratio():
            """Validates that the degree of change in the issue's description is less than allowed ratio.

            """
            # Escape if no change.
            if self.request.data['description'] == self.issue.description:
                return

            # Determine change ratio.
            diff = difflib.SequenceMatcher(None, self.issue.description, self.request.data['description'])
            diff_ratio = round(diff.ratio(), 3) * 100
            if diff_ratio < constants.DESCRIPTION_CHANGE_RATIO:
                raise exceptions.IssueDescriptionChangeRatioError(diff_ratio)


        def _validate_issue_status():
            """Validates that issue state allows it to be updated.

            """
            if self.issue.workflow != constants.WORKFLOW_NEW and \
               self.request.data['workflow'] == constants.WORKFLOW_NEW:
                raise exceptions.InvalidIssueStatusError()


        def _validate_request():
            """Validates incoming request prior to processing.

            """
            self.validate_request_json_headers()
            self.validate_request_params(None)
            self.validate_request_body(constants.JSON_SCHEMAS['update'])
            _validate_issue_exists()
            _validate_issue_immutable_attributes()
            _validate_issue_description_change_ratio()
            _validate_issue_status()


        def _persist_issue():
            """Persists issue data to dB.

            """
            pass


        def _persist_datasets():
            """Persists dataset data to database.

            """
            pass


        # Invoke tasks.
        self.invoke([
            _validate_request,
            _persist_issue,
            _persist_datasets
            ])
