import re
from difflib import SequenceMatcher

import pyessv
import tornado

from errata import db
from errata.utils import config
from errata.utils import constants
from errata.utils import exceptions
from errata.utils import http_security
from errata.utils.http import process_request
from errata.utils.publisher import get_institute
from errata.utils.publisher import get_institutes
from errata.utils.publisher import update_issue
from errata.utils.http_security import authorize
from errata.utils.validation import validate_url


class UpdateIssueRequestHandler(tornado.web.RequestHandler):
    """Publishing update issue handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        http_security.set_headers(self, True)


    def options(self):
        """HTTP OPTIONS handler.

        """
        self.set_status(204)
        self.set_default_headers()
        self.finish()


    def post(self):
        """HTTP POST handler.

        """
        def _validate_issue_datasets():
            """Validates datasets associated with incoming issue.

            """
            sanitized_datasets = [dt.strip().encode('ascii', 'ignore').decode('ascii')
                                  for dt in self.request.data[constants.JF_DATASETS]]
            if sanitized_datasets is None or sanitized_datasets == 0:
                raise exceptions.EmptyDatasetList()
            else:
                for dset in sanitized_datasets:
                    if re.search(constants.VERSION_REGEX, dset) is None:
                        raise exceptions.MissingVersionNumber(dset)
            try:
                pyessv.parse_dataset_identifers(
                    self.request.data[constants.JF_PROJECT],
                    sanitized_datasets
                    )
            except pyessv.TemplateParsingError:
                raise exceptions.InvalidDatasetIdentifierError(self.request.data[constants.JF_PROJECT])


        def _validate_issue_institute():
            """Validates datasets associated with incoming issue.

            """
            if len(get_institutes(self.request.data)) != 1:
                raise exceptions.MultipleInstitutesError()


        def _validate_user_access():
            """Validates user's institutional access rights.

            """
            if config.apply_security_policy:
                authorize(self.user_id, self.request.data[constants.JF_PROJECT], get_institute(self.request.data))


        def _validate_issue_exists():
            """Validates that the issue has been previously posted to the web-service.

            """
            self.issue = db.dao.get_issue(self.request.data[constants.JF_UID])
            if self.issue is None:
                raise exceptions.UnknownIssueError(self.request.data[constants.JF_UID])


        def _validate_issue_urls():
            """Validates URL's associated with incoming request.

            """
            urls = self.request.data[constants.JF_URLS] + self.request.data[constants.JF_MATERIALS]
            urls = [i for i in urls if i]
            for url in urls:
                validate_url(url)


        def _validate_issue_immutable_attributes():
            """Validates that issue attribute deemed to be immutable have not been changed.

            """
            # if self.issue.institute != get_institute(self.request.data):
            #     raise exceptions.IssueImmutableAttributeError('institute')
            for attr in constants.ISSUE_IMMUTABLE_ATTRIBUTES:
                if self.request.data[attr].lower() != getattr(self.issue, attr).lower():
                    raise exceptions.IssueImmutableAttributeError(attr)


        def _validate_issue_status():
            """Validates that issue status allows it to be updated.

            """
            if self.issue.status != constants.ISSUE_STATUS_NEW and self.request.data[constants.JF_STATUS] == constants.ISSUE_STATUS_NEW:
                raise exceptions.IssueStatusChangeError()


        def _validate_issue_description():
            """Validates URL's associated with incoming request.
            When an issue is updated, all descriptions in the db are dumped and compared to the new description.
            The new description needs to be different to existing descriptions by predefined ratio (in ws.conf).
            The updated description needs to also be no more different thant the original by a ratio that is also
            predefined in the ws.conf file.

            """
            # Testing incoming description to db existing descriptions.
            issue_description = self.request.data[constants.JF_DESCRIPTION]
            issue_uid = self.request.data[constants.JF_UID]
            # Check db for existing descriptions.
            existing_descriptions = db.dao.get_descriptions()
            for desc in existing_descriptions:
                # Making sure to discard the same issue from this test.
                if desc[1] != issue_uid:
                    s = SequenceMatcher(None, issue_description, desc[0])
                    if s.ratio() > config.allowed_description_similarity_ratio:
                        raise exceptions.SimilarIssueDescriptionError(desc[1])
            # Testing updated description to the db stored original description.
            issue = db.dao.get_issue(self.request.data[constants.JF_UID])
            s = SequenceMatcher(None, issue_description, issue.description)
            # Here the test is < since the update description can't be too different from the original one,
            # Otherwise users are asked to create a new issue altogether.
            if s.ratio() < config.allowed_description_update_similarity_ratio:
                raise exceptions.UpdatedDescriptionTooDifferentError(s.ratio())


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
                db.session.insert(entity, auto_commit=False)
            db.session.commit()

            # Update PID handle errata.
            dsets_new = db.dao.get_datasets(self.issue.uid)
            for action, identifiers in (
                (constants.PID_ACTION_DELETE, dsets_old - dsets_new),
                (constants.PID_ACTION_INSERT, dsets_new - dsets_old)
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
                # _validate_issue_description,
                _validate_issue_datasets,
                # _validate_issue_institute,
                _validate_user_access,
                _validate_issue_exists,
                _validate_issue_urls,
                _validate_issue_immutable_attributes,
                _validate_issue_status,
                _persist
            ])
