# -*- coding: utf-8 -*-

"""
.. module:: handlers.update.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - update issue endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import difflib

import tornado

from errata import db
from errata.utils import constants
from errata.utils import exceptions
from errata.utils.constants_json import *
from errata.utils.http import process_request



class UpdateIssueRequestHandler(tornado.web.RequestHandler):
    """issue handler.

    """
    def post(self):
        """HTTP POST handler.

        """
        def _validate_issue_exists():
            """Validates that the issue has been previously posted to the web-service.

            """
            issue = self.issue = db.dao.get_issue(self.request.data[JF_UID])
            if issue is None:
                raise exceptions.UnknownIssueError(self.request.data[JF_UID])


        def _validate_issue_immutable_attributes():
            """Validates that issue attribute deemed to be immutable have not been changed.

            """
            for attr_name in constants.IMMUTABLE_ISSUE_ATTRIBUTES:
                if unicode(self.request.data[attr_name]).lower() != unicode(getattr(self.issue, attr_name)).lower():
                    raise exceptions.ImmutableIssueAttributeError(attr_name)
            print "TODO: validate dateCreated immutability"


        def _validate_issue_description_change_ratio():
            """Validates that the degree of change in the issue's description is less than allowed ratio.

            """
            # Escape if no change.
            if self.request.data[JF_DESCRIPTION] == self.issue.description:
                return

            # Determine change ratio.
            diff = difflib.SequenceMatcher(None, self.issue.description, self.request.data[JF_DESCRIPTION])
            diff_ratio = round(diff.ratio(), 3) * 100
            if diff_ratio < constants.DESCRIPTION_CHANGE_RATIO:
                raise exceptions.IssueDescriptionChangeRatioError(diff_ratio)


        def _validate_issue_status():
            """Validates that issue status allows it to be updated.

            """
            if self.issue.status != constants.STATUS_NEW and \
               self.request.data[JF_STATUS] == constants.STATUS_NEW:
                raise exceptions.InvalidIssueStatusError()


        def _persist():
            """Persists dB changes.

            """
            obj = self.request.data
            # Update issue.
            issue = self.issue
            issue.date_closed = obj.get(JF_DATE_CLOSED)
            issue.closed_by = obj.get(JF_CLOSED_BY)
            issue.description = obj[JF_DESCRIPTION]
            issue.materials = ",".join(obj.get(JF_MATERIALS, []))
            issue.severity = obj[JF_SEVERITY].lower()
            issue.title = obj[JF_TITLE]
            issue.date_updated = obj[JF_DATE_UPDATED]
            issue.updated_by = obj[JF_UPDATED_BY]
            issue.url = obj.get(JF_URL)
            issue.status = obj[JF_STATUS].lower()

            # Delete existing facets.
            db.dao.delete_facets(issue.uid)

            # Insert facets.
            for facet_type in constants.FACET_TYPE:
                facet_ids = self.request.data.get('{}s'.format(facet_type), [])
                for facet_id in facet_ids:
                    facet = db.models.IssueFacet()
                    facet.facet_id = facet_id
                    facet.facet_type = facet_type
                    facet.issue_uid = self.issue.uid
                    db.session.insert(facet, False)

        # Process request.
        with db.session.create(commitable=True):
            process_request(self, [
                _validate_issue_exists,
                _validate_issue_immutable_attributes,
                _validate_issue_description_change_ratio,
                _validate_issue_status,
                _persist
                ])
