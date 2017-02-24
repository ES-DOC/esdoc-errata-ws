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

from errata.db.dao import get_issue
from errata.db.dao import get_issue_facets
from errata.db.dao import delete_facets
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
            issue = self.issue = get_issue(self.request.data[JF_UID])
            if issue is None:
                raise exceptions.UnknownIssueError(self.request.data[JF_UID])


        def _validate_user_access():
            """Validates user's institutional access rights.

            """
            # Super & insitutional users have access.
            for team in sorted(self.user_teams):
                if team == constants.ERRATA_GH_TEAM:
                    return
                if team.split("-")[-1] == self.issue.institute.lower():
                    return

            # User has no access rights to this particular issue.
            raise exceptions.AuthorizationError()


        def _validate_issue_immutable_attributes():
            """Validates that issue attribute deemed to be immutable have not been changed.

            """
            for attr_name in constants.IMMUTABLE_ISSUE_ATTRIBUTES:
                if unicode(self.request.data[attr_name]).lower() != unicode(getattr(self.issue, attr_name)).lower():
                    raise exceptions.ImmutableIssueAttributeError(attr_name)
            # print "TODO: validate dateCreated immutability"


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


        def _persist_pid_tasks():
            """Persists pid handles.

            """
            # Set existing datasets.
            dsets_existing = get_issue_facets(self.issue.uid, constants.FACET_TYPE_DATASET)
            dsets_existing = set([i.facet_value for i in dsets_existing])

            # Set actual datasets.
            dsets_actual = set(self.request.data[JF_DATASETS])

            # Remove obsolete PID handle errata.
            for action, dsets in (
                (constants.PID_ACTION_DELETE, list(dsets_existing - dsets_actual)),
                (constants.PID_ACTION_INSERT, list(dsets_actual - dsets_existing)),
                ):
                print 666, action, len(dsets)
                for dset in dsets:
                    task = db.models.PIDServiceTask()
                    task.action = action
                    task.issue_uid = self.issue.uid
                    task.dataset_id = dset
                    db.session.insert(task, False)


        def _persist_issue():
            """Persists issue update.

            """
            obj = self.request.data
            issue = self.issue
            issue.date_closed = obj.get(JF_DATE_CLOSED)
            issue.description = obj[JF_DESCRIPTION]
            issue.materials = ",".join(obj.get(JF_MATERIALS, []))
            issue.severity = obj[JF_SEVERITY].lower()
            issue.title = obj[JF_TITLE]
            issue.date_updated = obj[JF_DATE_UPDATED]
            issue.updated_by = self.user_name
            issue.url = obj.get(JF_URL)
            issue.status = obj[JF_STATUS].lower()


        def _persist_facets():
            """Insert new facets.

            """
            # Reset existing.
            delete_facets(self.issue.uid)

            # Iterate facet types:
            for ft in constants.FACET_TYPE:
                # ... set facet values.
                fv_list = self.request.data[FACET_TYPE_JSON_FIELD[ft]]
                if not isinstance(fv_list, list):
                    fv_list = [fv_list]
                fv_list = [i for i in fv_list if i and len(i.strip()) > 0]

                # ... persist facets.
                for fv in set(fv_list):
                    f = db.models.IssueFacet()
                    f.facet_value = fv.strip()
                    f.facet_type = ft
                    f.issue_uid = self.issue.uid
                    db.session.insert(f, False)


        # Process request.
        with db.session.create(commitable=True):
            process_request(self, [
                _validate_issue_exists,
                _validate_user_access,
                _validate_issue_immutable_attributes,
                _validate_issue_description_change_ratio,
                _validate_issue_status,
                _persist_pid_tasks,
                _persist_issue,
                _persist_facets
                ])
