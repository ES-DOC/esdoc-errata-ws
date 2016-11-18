# -*- coding: utf-8 -*-

"""
.. module:: handlers.create.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - create issue endpoint.

.. module author:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import sqlalchemy
import tornado

from errata import db
from errata.utils import constants
from errata.utils.http import process_request
from errata.utils.misc import traverse
from errata.utils.validation import validate_url


class CreateIssueRequestHandler(tornado.web.RequestHandler):
    """issue handler.

    """
    def post(self):
        """HTTP POST handler.

        """
        def _validate_issue_urls():
            """Validates URL's associated with incoming request.

            """
            for url in traverse([self.request.data.get((i)) for i in ['url', 'materials']]):
                validate_url(url)

        def _set_issue():
            """Creates issue.

            """
            self.issue = issue = db.models.Issue()
            issue.date_closed = self.request.data.get('dateClosed')
            issue.date_created = self.request.data['dateCreated']
            issue.date_updated = self.request.data.get('dateUpdated', issue.date_created)
            issue.description = self.request.data['description']
            issue.institute = self.request.data['institute'].lower()
            issue.materials = ",".join(self.request.data.get('materials', []))
            issue.project = self.request.data['project'].lower()
            issue.severity = self.request.data['severity'].lower()
            issue.title = self.request.data['title']
            issue.uid = self.request.data['uid']
            issue.url = self.request.data.get('url')
            issue.status = self.request.data['status'].lower()

        def _set_facets():
            """Sets search facets to be persisted to database.

            """
            self.facets = facets = []
            for facet_type in constants.FACET_TYPE:
                facet_ids = self.request.data.get('{}s'.format(facet_type), [])
                for facet_id in facet_ids:
                    facet = db.models.IssueFacet()
                    facet.facet_id = facet_id
                    facet.facet_type = facet_type
                    facet.issue_uid = self.issue.uid
                    facets.append(facet)

        def _persist():
            """Persists data to dB.

            """
            # Persist issue.
            with db.session.create():
                try:
                    db.session.insert(self.issue)
                except sqlalchemy.exc.IntegrityError:
                    db.session.rollback()
                    raise ValueError("Issue description/uid fields must be unique")

            # Persist facets.
            with db.session.create(commitable=True):
                for facet in self.facets:
                    db.session.insert(facet, False)

        # Process request.
        process_request(self, [
            _validate_issue_urls,
            _set_issue,
            _set_facets,
            _persist
            ])
