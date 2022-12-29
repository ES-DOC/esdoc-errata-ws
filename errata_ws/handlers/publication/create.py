import re
from difflib import SequenceMatcher

import pyessv
import tornado

from errata_ws import db
from errata_ws.utils import config
from errata_ws.utils import constants
from errata_ws.utils import exceptions
from errata_ws.utils import http_security
from errata_ws.utils.http import process_request
from errata_ws.utils.http_security import authorize
from errata_ws.utils.publisher import create_issue
from errata_ws.utils.publisher import get_institute
from errata_ws.utils.publisher import get_institutes
from errata_ws.utils.validation import validate_url


class CreateErrataRequestHandler(tornado.web.RequestHandler):
    """Publishing create issue handler.

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
            sanitzed_datasets = [dset.strip().encode('ascii', 'ignore').decode('ascii')
                                 for dset in self.request.data[constants.JF_DATASETS]]
            if sanitzed_datasets is None or len(sanitzed_datasets) == 0:
                raise exceptions.EmptyDatasetList()

            for dset in sanitzed_datasets:
                if re.search(constants.VERSION_REGEX, dset) is None:
                    raise exceptions.MissingVersionNumber(dset)

            try:
                pyessv.parse_dataset_identifers(
                    self.request.data[constants.JF_PROJECT],
                    sanitzed_datasets
                )
            except pyessv.TemplateParsingError:
                raise exceptions.InvalidDatasetIdentifierError(self.request.data[constants.JF_PROJECT])


        def _validate_user_access():
            """Validates user's institutional access rights.

            """
            if config.apply_security_policy:
                authorize(self.user_id, self.request.data[constants.JF_PROJECT], get_institute(self.request.data))


        def _validate_issue_title():
            """Validates URL's associated with incoming request.

            """
            # Check db for existing titles.
            issue_title = self.request.data[constants.JF_TITLE]
            with db.session.create():
                existing_titles = db.dao.get_titles()
                if issue_title in existing_titles:
                    raise exceptions.TitleExistsError(issue_title)


        def _validate_issue_urls():
            """Validates URL's associated with incoming request.

            """
            urls = self.request.data[constants.JF_URLS] + self.request.data[constants.JF_MATERIALS]
            urls = [i for i in urls if i]
            for url in urls:
                validate_url(url)


        def _persist():
            """Persists data to dB.

            """
            with db.session.create():
                # Map request data to db entities.
                entities = create_issue(self.request.data, self.user_id)

                # Insert issue first so that the foreign keys can be established.
                db.session.insert(entities[0])

                # Insert facets/resources/pid-tasks.
                for entity in entities[1:]:
                    db.session.insert(entity, auto_commit=False)
                
                # Commit atomic transation.
                db.session.commit()


        # Process request.
        process_request(self, [
            _validate_issue_title,
            _validate_issue_datasets,
            _validate_user_access,
            _validate_issue_urls,
            _persist
        ])

