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
from errata.utils.pid_connector import create_connector, add_errata_to_handle, remove_errata_from_handle




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
            """Persists facets.

            """
            obj = self.request.data

            # Delete existing facets.
            db.dao.delete_facets(self.issue.uid)

            # Insert new facets.
            for facet_type in constants.FACET_TYPE:
                # Set facet values.
                if facet_type in obj and facet_type not in constants.MULTIPLE_FACETS:
                    facet_values = [obj[facet_type]]
                else:
                    facet_values = obj.get('{}s'.format(facet_type), [])
                facet_values = [i for i in facet_values if i and len(i) > 0]

                # Insert new facets.
                for facet_value in set(facet_values):
                    facet = db.models.IssueFacet()
                    facet.facet_value = facet_value
                    facet.facet_type = facet_type
                    facet.issue_uid = self.issue.uid
                    db.session.insert(facet, False)

        def _update_pids():
            """
            updates handles at the pid server.

            """
            # Retrieving the new dataset list and the issue uid from the request.
            obj = self.request.data
            if constants.DATASETS in obj and constants.UID in obj:
                new_datasets = obj[constants.DATASETS]
                uid = obj[constants.UID]
            else:
                raise exceptions.InvalidJSONSchemaError
            # Retrieving the old dataset list from database
            old_facets = db.dao.get_facets(self.issue.uid)
            old_datasets = []
            for facet in old_facets:
                if facet.facet_type == constants.FACET_TYPE_DATASET:
                    old_datasets.append(facet.facet_value)
            connector = create_connector()
            connector.start_messaging_thread()
            for dset in list(set(old_datasets)-set(new_datasets)):
                remove_errata_from_handle(dset, uid, connector)
            for dset in list(set(new_datasets)-set(old_datasets)):
                add_errata_to_handle(dset, uid, connector)
            connector.finish_messaging_thread()



        # Process request.
        with db.session.create(commitable=True):
            process_request(self, [
                _validate_issue_exists,
                _validate_user_access,
                _validate_issue_immutable_attributes,
                _validate_issue_description_change_ratio,
                _validate_issue_status,
                _update_pids,
                _persist_issue,
                _persist_facets
                ])
