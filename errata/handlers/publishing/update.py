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
from errata.utils.pid_connector import add_errata_to_handle
from errata.utils.pid_connector import create_connector
from errata.utils.pid_connector import remove_errata_from_handle



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


        def _update_pids():
            """Updates handles at the pid server.

            """
            # Set existing datasets.
            dsets_existing = set([i.facet_value for i in db.dao.get_issue_facets(self.issue.uid, constants.FACET_TYPE_DATASET)])

            # Set actual datasets.
            dsets_actual = set(self.request.data[JF_DATASETS])

            # Set obsolete datasets.
            dsets_obsolete = list(dsets_existing - dsets_actual)

            # Set new datasets.
            dsets_new = list(dsets_actual - dsets_existing)

            # Establish PID service connection.
            connector = create_connector()
            connector.start_messaging_thread()

            # Remove obsolete PID handle errata.
            for dset in  list(dsets_existing - dsets_actual):
                remove_errata_from_handle(dset, self.request.data[JF_UID], connector)

            # Insert new PID handle errata.
            for dset in list(dsets_actual - dsets_existing):
                add_errata_to_handle(dset, self.request.data[JF_UID], connector)

            # Kill PID service connection.
            connector.finish_messaging_thread()


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


        def _reset_facets():
            """Delete existing facets.

            """
            db.dao.delete_facets(self.issue.uid)


        def _persist_facets():
            """Insert new facets.

            """
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
                # _update_pids,
                _persist_issue,
                _reset_facets,
                _persist_facets
                ])
