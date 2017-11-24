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
from errata.utils.constants import IMMUTABLE_ISSUE_ATTRIBUTES
from errata.utils.constants import PID_ACTION_DELETE
from errata.utils.constants import PID_ACTION_INSERT
from errata.utils.constants import STATUS_NEW
from errata.utils.constants_json import JF_DATASETS
from errata.utils.constants_json import JF_DESCRIPTION
from errata.utils.constants_json import JF_MATERIALS
from errata.utils.constants_json import JF_PROJECT
from errata.utils.constants_json import JF_STATUS
from errata.utils.constants_json import JF_UID
from errata.utils.constants_json import JF_URLS
from errata.utils.http import process_request
from errata.utils.publisher import get_institute
from errata.utils.publisher import get_institutes
from errata.utils.publisher import update_issue
from errata.utils.http_security import authorize
from errata.utils.validation import validate_url



class UpdateIssueRequestHandler(tornado.web.RequestHandler):
    """issue handler.

    """

    def post(self):
        """HTTP POST handler.

        """
        def _validate_issue_datasets():
            """Validates datasets associated with incoming issue.

            """
            pyessv.parse_dataset_identifers(
                self.request.data[JF_PROJECT],
                self.request.data[JF_DATASETS]
                )


        def _validate_issue_institute():
            """Validates datasets associated with incoming issue.

            """
            if len(get_institutes(self.request.data)) != 1:
                raise ValueError('Multiple insitiute codes are not supported')


        def _validate_user_access():
            """Validates user's institutional access rights.

            """
            if config.apply_security_policy:
                authorize(self.user_id, self.request.data[JF_PROJECT], get_institute(self.request.data))


        def _validate_issue_exists():
            """Validates that the issue has been previously posted to the web-service.

            """
            self.issue = db.dao.get_issue(self.request.data[JF_UID])
            if self.issue is None:
                raise exceptions.UnknownIssueError(self.request.data[JF_UID])


        def _validate_issue_urls():
            """Validates URL's associated with incoming request.

            """
            if config.validate_issue_urls:
                urls = self.request.data[JF_URLS] + self.request.data[JF_MATERIALS]
                urls = [i for i in urls if i]
                for url in urls:
                    validate_url(url)


        def _validate_issue_immutable_attributes():
            """Validates that issue attribute deemed to be immutable have not been changed.

            """
            if self.issue.institute != get_institute(self.request.data):
                raise exceptions.ImmutableIssueAttributeError('institute')
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
            # Get old datasets.
            dsets_old = db.dao.get_datasets(self.issue.uid)

            # Delete existing facets / resources.
            db.dao.delete_facets(self.issue.uid)
            db.dao.delete_resources(self.issue.uid)

            # Update issue.
            for entity in update_issue(self.issue, self.request.data, self.user_id):
                db.session.insert(entity)

            # Update PID handle errata.
            dsets_new = db.dao.get_datasets(self.issue.uid)
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
                _validate_issue_datasets,
                _validate_issue_institute,
                _validate_user_access,
                _validate_issue_exists,
                _validate_issue_urls,
                _validate_issue_immutable_attributes,
                _validate_issue_description_change_ratio,
                _validate_issue_status,
                _persist
            ])
