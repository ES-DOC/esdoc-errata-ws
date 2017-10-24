# -*- coding: utf-8 -*-

"""
.. module:: handlers.update.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - update issue endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import difflib
import os
import tornado
import re

import pyessv

from errata import db

from errata.db.dao import get_issue
from errata.db.dao import get_facets
from errata.db.dao import delete_facets
from errata.utils import config
from errata.utils import config_esg
from errata.utils import constants
from errata.utils import exceptions
from errata.utils import logger
from errata.utils.constants_json import *
from errata.utils.http import process_request



class UpdateIssueRequestHandler(tornado.web.RequestHandler):
    """issue handler.

    """

    def post(self):
        """HTTP POST handler.

        """
        def _validate_project():
            """Validates project is supported.

            """
            self.project = self.request.data[JF_PROJECT]
            self.project_conf = config_esg.get_active_project(self.project)
            if self.project_conf is None:
                raise exceptions.UnknownProjectError(self.project)


        def _validate_issue_exists():
            """Validates that the issue has been previously posted to the web-service.

            """
            self.issue = get_issue(self.request.data[JF_UID])
            if self.issue is None:
                raise exceptions.UnknownIssueError(self.request.data[JF_UID])


        def _validate_issue_facets():
            """Validates facets associated with incoming issue.

            """
            # Assert: facets are supported.
            for facet_type in self.request.data[JF_FACETS]:
                if facet_type not in self.project_conf['facets']:
                    raise exceptions.UnknownFacetError(self.project, facet_type)

            # Assert: facet values are valid.
            for facet_type, facet_values in self.request.data[JF_FACETS].items():
                facet_conf = self.project_conf['facets'][facet_type]
                collection_namespace = facet_conf['collection'].namespace
                for facet_value in facet_values:
                    facet_namespace = '{}:{}'.format(collection_namespace, facet_value)
                    if pyessv.parse_namespace(facet_namespace, strictness=3) is None:
                        raise exceptions.InvalidFacetError(self.project, facet_type, facet_value)


        def _validate_issue_urls():
            """Validates URL's associated with incoming request.

            """
            if config.apply_security_policy:
                urls = [self.request.data.get(i) for i in [JF_URL, JF_MATERIALS]]
                for url in traverse(urls):
                    validate_url(url)


        def _validate_issue_immutable_attributes():
            """Validates that issue attribute deemed to be immutable have not been changed.

            """
            for attr in constants.IMMUTABLE_ISSUE_ATTRIBUTES:
                if self.request.data[attr].lower() != getattr(self.issue, attr).lower():
                    raise exceptions.ImmutableIssueAttributeError(attr)


        def _validate_issue_description_change_ratio():
            """Validates that the degree of change in the issue's description is less than allowed ratio.

            """
            # Escape if no change.
            if self.request.data[JF_DESCRIPTION] == self.issue.description:
                return

            # Determine change ratio.
            diff = difflib.SequenceMatcher(None, self.issue.description, self.request.data[JF_DESCRIPTION])
            diff_ratio = 100 - round(diff.ratio(), 3) * 100
            if diff_ratio > constants.DESCRIPTION_CHANGE_RATIO:
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
            if self.project_conf['is_pid_client']:
                # Set existing datasets.
                print 111, self.issue.uid
                dsets_existing = get_facets(issue_uid=self.issue.uid, facet_type=constants.FACET_TYPE_DATASET)
                dsets_existing = set([i.facet_value for i in dsets_existing])

                # Set actual datasets.
                dsets_actual = set(self.request.data[JF_DATASETS])

                print 666, dsets_existing
                print 777, dsets_actual

                return

                # Remove obsolete PID handle errata.
                for action, dsets in (
                    (constants.PID_ACTION_DELETE, list(dsets_existing - dsets_actual)),
                    (constants.PID_ACTION_INSERT, list(dsets_actual - dsets_existing)),
                ):
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
            issue.updated_by = self.user_id
            issue.url = obj.get(JF_URL)
            issue.status = obj[JF_STATUS].lower()


        def _persist_facets():
            """Insert new facets.

            """
            delete_facets(self.issue.uid)
            for facet_type, facet_values in self.request.data[JF_FACETS].items():
                for facet_value in set(facet_values):
                    facet = db.models.IssueFacet()
                    facet.facet_type = facet_type
                    facet.facet_value = facet_value.strip()
                    facet.issue_uid = self.issue.uid
                    db.session.insert(facet, False)


        # Process request.
        with db.session.create(commitable=True):
            process_request(self, [
                _validate_project,
                _validate_issue_exists,
                _validate_issue_facets,
                _validate_issue_urls,
                _validate_issue_immutable_attributes,
                _validate_issue_description_change_ratio,
                _validate_issue_status,
                _persist_pid_tasks,
                _persist_issue,
                _persist_facets
            ])
