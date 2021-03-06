# -*- coding: utf-8 -*-

"""
.. module:: handlers.create.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - create issue endpoint.

.. module author:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import tornado
import re
import pyessv
from difflib import SequenceMatcher

from errata import db
from errata.utils import config
from errata.utils import constants
from errata.utils import exceptions
from errata.utils import security
from errata.utils.constants import *
from errata.utils.http import process_request
from errata.utils.http_security import authorize
from errata.utils.publisher import create_issue
from errata.utils.publisher import get_institute
from errata.utils.publisher import get_institutes
from errata.utils.validation import validate_url


class CreateIssueRequestHandler(tornado.web.RequestHandler):
    """issue handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(constants.HTTP_HEADER_Access_Control_Allow_Origin, "*")
        self.set_header("Access-Control-Allow-Headers", "content-type, Authorization")
        self.set_header('Access-Control-Allow-Methods', 'POST')
        self.set_header('Access-Control-Allow-Credentials', True)
        self.set_header('X-XSRFToken', self.xsrf_token)


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
                                 for dset in self.request.data[JF_DATASETS]]
            if sanitzed_datasets is None or len(sanitzed_datasets) == 0:
                raise exceptions.EmptyDatasetList()

            for dset in sanitzed_datasets:
                if re.search(VERSION_REGEX, dset) is None:
                    raise exceptions.MissingVersionNumber(dset)

            try:
                pyessv.parse_dataset_identifers(
                    self.request.data[JF_PROJECT],
                    sanitzed_datasets
                )
            except pyessv.TemplateParsingError:
                raise exceptions.InvalidDatasetIdentifierError(self.request.data[JF_PROJECT])


        def _validate_issue_institute():
            """Validates datasets associated with incoming issue.

            """
            if len(get_institutes(self.request.data)) != 1:
                raise exceptions.MultipleInstitutesError()


        def _validate_user_access():
            """Validates user's institutional access rights.

            """
            if config.apply_security_policy:
                authorize(self.user_id, self.request.data[JF_PROJECT], get_institute(self.request.data))


        def _validate_issue_title():
            """Validates URL's associated with incoming request.

            """
            # Check db for existing titles.
            issue_title = self.request.data[JF_TITLE]
            with db.session.create():
                existing_titles = db.dao.get_titles()
                if issue_title in existing_titles:
                    raise exceptions.TitleExistsError(issue_title)


        def _validate_issue_description():
            """Validates URL's associated with incoming request.
            When an issue is created, all descriptions in the db are dumped and compared to the new description.
            The new description needs to be different to existing descriptions by predefined ratio (in ws.conf).

            """
            # Check db for existing descriptions.
            issue_description = self.request.data[JF_DESCRIPTION]
            with db.session.create():
                existing_descriptions = db.dao.get_descriptions()
                for desc in existing_descriptions:
                    s = SequenceMatcher(None, issue_description, desc[0])
                    similarity_ratio = s.ratio()
                    if similarity_ratio > config.allowed_description_similarity_ratio:
                        raise exceptions.SimilarIssueDescriptionError(desc[1])


        def _validate_issue_urls():
            """Validates URL's associated with incoming request.

            """
            urls = self.request.data[JF_URLS] + self.request.data[JF_MATERIALS]
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
            # _validate_issue_description,
            _validate_issue_datasets,
            # _validate_issue_institute,
            _validate_user_access,
            _validate_issue_urls,
            _persist
        ])


dset = 'CMIP6.PMIP.AWI.AWI-ESM-1-1-LR.lig127k.r1i1p1f1.SImon.sifllatstop.gn#20200212'

if re.search(VERSION_REGEX, dset) is None:
    raise exceptions.MissingVersionNumber()