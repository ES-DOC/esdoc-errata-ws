# -*- coding: utf-8 -*-

"""
.. module:: handlers.create.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - create issue endpoint.

.. module author:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import tornado

import pyessv

from errata import db
from errata.utils import config
from errata.utils import config_esg
from errata.utils import constants
from errata.utils import factory
from errata.utils.constants_json import JF_DATASETS
from errata.utils.constants_json import JF_MATERIALS
from errata.utils.constants_json import JF_PROJECT
from errata.utils.constants_json import JF_URLS
from errata.utils.http import process_request
from errata.utils.publisher import create_issue
from errata.utils.publisher import get_institute
from errata.utils.publisher import get_institutes
from errata.utils.http_security import authorize
from errata.utils.validation import validate_url



class CreateIssueRequestHandler(tornado.web.RequestHandler):
    """issue handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(constants.HTTP_HEADER_Access_Control_Allow_Origin, "*")
        self.set_header("Access-Control-Allow-Headers", "content-type, Authorization")
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.set_header('Access-Control-Allow-Credentials', True)


    def options(self):
        """HTTP OPTIONS handler.

        """
        self.set_status(204)
        self.finish()


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


        def _validate_issue_urls():
            """Validates URL's associated with incoming request.

            """
            if config.validate_issue_urls:
                urls = self.request.data[JF_URLS] + self.request.data[JF_MATERIALS]
                urls = [i for i in urls if i]
                for url in urls:
                    validate_url(url)


        def _persist():
            """Persists data to dB.

            """
            with db.session.create():
                for entity in create_issue(self.request.data, self.user_id):
                    db.session.insert(entity)


        # Process request.
        process_request(self, [
            _validate_issue_datasets,
            _validate_issue_institute,
            _validate_user_access,
            _validate_issue_urls,
            _persist
        ])
