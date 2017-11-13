# -*- coding: utf-8 -*-

"""
.. module:: handlers.create.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - create issue endpoint.

.. module author:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import tornado

from errata import db
from errata.utils import config
from errata.utils import config_esg
from errata.utils import constants
from errata.utils import factory
from errata.utils.constants_json import JF_FACETS
from errata.utils.constants_json import JF_MATERIALS
from errata.utils.constants_json import JF_PROJECT
from errata.utils.constants_json import JF_URLS
from errata.utils.http import process_request
from errata.utils.publisher import create_issue
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
        def _validate_issue_facets():
            """Validates facets associated with incoming issue.

            """
            config_esg.validate(self.request.data[JF_PROJECT], self.request.data[JF_FACETS])


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
            # Decode from request.
            issue, facets, pid_tasks = \
                create_issue(self.request.data, self.user_id)

            # Persist to dB.
            db.session.insert(issue)
            for facet in facets:
                db.session.insert(facet)
            for pid_task in pid_tasks:
                db.session.insert(pid_task)


        # Process request.
        with db.session.create(commitable=True):
            process_request(self, [
                _validate_issue_facets,
                _validate_issue_urls,
                _persist
            ])
