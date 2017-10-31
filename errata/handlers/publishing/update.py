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

import pyessv

from errata import db
from errata.utils import config
from errata.utils import config_esg
from errata.utils import exceptions
from errata.utils import logger
from errata.utils.constants import DESCRIPTION_CHANGE_RATIO
from errata.utils.constants import FACET_TYPE_DATASET
from errata.utils.constants import IMMUTABLE_ISSUE_ATTRIBUTES
from errata.utils.constants import PID_ACTION_DELETE
from errata.utils.constants import PID_ACTION_INSERT
from errata.utils.constants import STATUS_NEW
from errata.utils.constants_json import JF_DESCRIPTION
from errata.utils.constants_json import JF_FACETS
from errata.utils.constants_json import JF_MATERIALS
from errata.utils.constants_json import JF_PROJECT
from errata.utils.constants_json import JF_STATUS
from errata.utils.constants_json import JF_UID
from errata.utils.constants_json import JF_URL
from errata.utils.http import process_request
from errata.utils.publisher import update_issue
from errata.utils.validation import validate_url



class UpdateIssueRequestHandler(tornado.web.RequestHandler):
    """issue handler.

    """

    def post(self):
        """HTTP POST handler.

        """
        def _validate_issue_facets():
            """Validates facets associated with incoming issue.

            """
            config_esg.validate(self.request.data[JF_PROJECT], self.request.data[JF_FACETS])


        def _validate_issue_exists():
            """Validates that the issue has been previously posted to the web-service.

            """
            self.issue = db.dao.get_issue(self.request.data[JF_UID])
            if self.issue is None:
                raise exceptions.UnknownIssueError(self.request.data[JF_UID])


        def _validate_issue_urls():
            """Validates URL's associated with incoming request.

            """
            if config.apply_security_policy:
                urls = [self.request.data[JF_URL]] + self.request.data[JF_MATERIALS]
                urls = [i for i in urls if i]
                for url in urls:
                    validate_url(url)


        def _validate_issue_immutable_attributes():
            """Validates that issue attribute deemed to be immutable have not been changed.

            """
            for attr in IMMUTABLE_ISSUE_ATTRIBUTES:
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
            if diff_ratio > DESCRIPTION_CHANGE_RATIO:
                raise exceptions.IssueDescriptionChangeRatioError(diff_ratio)


        def _validate_issue_status():
            """Validates that issue status allows it to be updated.

            """
            if self.issue.status != STATUS_NEW and self.request.data[JF_STATUS] == STATUS_NEW:
                raise exceptions.InvalidIssueStatusError()


        def _persist():
            """Persists data to dB.

            """
            # Set old datasets.
            dsets_old = db.dao.get_facets(issue_uid=self.issue.uid, facet_type=FACET_TYPE_DATASET)
            dsets_old = set([i.facet_value for i in dsets_old])

            # Delete old facets.
            db.dao.delete_facets(self.issue.uid)

            # Update issue & insert new facets.
            facets = update_issue(self.issue, self.request.data, self.user_id)
            for facet in facets:
                db.session.insert(facet)

            # Update PID handle errata.
            dsets_new = set([i.facet_value for i in facets if i.facet_type == FACET_TYPE_DATASET])
            for action, identifiers in (
                (PID_ACTION_DELETE, dsets_old - dsets_new),
                (PID_ACTION_INSERT, dsets_new - dsets_old)
            ):
                for identifier in identifiers:
                    task = db.models.PIDServiceTask()
                    task.action = action
                    task.issue_uid = self.issue.uid
                    task.dataset_id = identifier
                    db.session.insert(task, False)


        # Process request.
        with db.session.create(commitable=True):
            process_request(self, [
                _validate_issue_facets,
                _validate_issue_exists,
                _validate_issue_urls,
                _validate_issue_immutable_attributes,
                _validate_issue_description_change_ratio,
                _validate_issue_status,
                _persist
            ])
