import re
from difflib import SequenceMatcher

import pyessv
import tornado

from errata import db
from errata import notifications
from errata.utils import config
from errata.utils import constants
from errata.utils import exceptions
from errata.utils import http_security
from errata.utils.http import process_request
from errata.utils.publisher import get_proposed_issue_entities
from errata.utils.publisher import get_institutes
from errata.utils.validation import validate_url


class ProposeIssueRequestHandler(tornado.web.RequestHandler):
    """issue handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        http_security.set_headers(self, True)


    def post(self):
        """HTTP POST handler.

        """
        def _validate_issue_datasets():
            """Validates datasets associated with incoming issue.

            """
            # Exception if no usable dataset identifiers.
            dsets_sanitized = [
                dset.strip().encode('ascii', 'ignore').decode('ascii')
                for dset in self.request.data[constants.JF_DATASETS]
                ]
            if dsets_sanitized is None or len(dsets_sanitized) == 0:
                raise exceptions.EmptyDatasetList()

            # Exception if dataset version is missing.
            for dset in dsets_sanitized:
                if re.search(constants.VERSION_REGEX, dset) is None:
                    raise exceptions.MissingVersionNumber(dset)

            # Exception if pyessv dataset parsing fails.
            try:
                pyessv.parse_dataset_identifers(
                    self.request.data[constants.JF_PROJECT],
                    dsets_sanitized
                )
            except pyessv.TemplateParsingError:
                raise exceptions.InvalidDatasetIdentifierError(self.request.data[constants.JF_PROJECT])


        def _validate_issue_title():
            """Validates URL's associated with incoming request.

            """
            # Exception if duplicate title.
            issue_title = self.request.data[constants.JF_TITLE]
            with db.session.create():
                existing_titles = db.dao.get_titles()
                if issue_title in existing_titles:
                    raise exceptions.TitleExistsError(issue_title)


        def _validate_issue_urls():
            """Validates URL's associated with incoming request.

            """
            # Exception if an associated issue URL is invalid.
            urls = self.request.data[constants.JF_URLS] + self.request.data[constants.JF_MATERIALS]
            urls = [i for i in urls if i]
            for url in urls:
                validate_url(url)


        def _persist():
            """Persists data to dB.

            """
            with db.session.create(commitable=True):
                # Map request data to db entities.
                entities = get_proposed_issue_entities(self.request.data, self.request.data["userEmail"])

                # Insert errata.
                db.session.insert(entities[0])

                # Insert associated entities (facets/resources/pid-tasks).
                for entity in entities[1:]:
                    db.session.insert(entity, auto_commit=False)
                
                # Make available downstream.
                self.issue = entities[0]


        def _notify():
            """Notifies proposer & moderation team.

            """
            notifications.dispatch_on_proposed(
                self.issue.created_by,
                self.issue.uid
            )


        # Process request.
        process_request(self, [
            _validate_issue_title,
            _validate_issue_datasets,
            _validate_issue_urls,
            _persist,
            _notify
        ])
