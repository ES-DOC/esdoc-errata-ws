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
from errata.utils import exceptions
from errata.utils.constants_json import *
from errata.utils.http import process_request
from errata.utils.misc import traverse
from errata.utils.validation import validate_url



class CreateIssueRequestHandler(tornado.web.RequestHandler):
    """issue handler.

    """
    def post(self):
        """HTTP POST handler.

        """
        def _validate_user_access():
            """Validates user's institutional access rights.

            """
            # Super & insitutional users have access.
            for team in sorted(self.user_teams):
                if team == constants.ERRATA_GH_TEAM:
                    return
                if team.split("-")[-1] == self.request.data[JF_INSTITUTE].lower():
                    return

            # User has no access rights to this particular issue.
            raise exceptions.AuthorizationError()


        def _validate_issue_urls():
            """Validates URL's associated with incoming request.

            """
            urls = traverse([self.request.data.get((i)) for i in [JF_URL, JF_MATERIALS]])
            for url in urls:
                validate_url(url)

        def _set_issue():
            """Creates issue.

            """
            obj = self.request.data
            self.issue = issue = db.models.Issue()
            issue.date_closed = obj.get(JF_DATE_CLOSED)
            issue.date_created = obj[JF_DATE_CREATED]
            issue.created_by = self.user_name
            issue.description = obj[JF_DESCRIPTION]
            issue.institute = obj[JF_INSTITUTE].lower()
            issue.materials = ",".join(obj.get(JF_MATERIALS, []))
            issue.project = obj[JF_PROJECT].lower()
            issue.severity = obj[JF_SEVERITY].lower()
            issue.title = obj[JF_TITLE]
            issue.uid = obj[JF_UID]
            issue.date_updated = obj.get(JF_DATE_UPDATED, issue.date_created)
            issue.updated_by = self.user_name
            issue.url = obj.get(JF_URL)
            issue.status = obj[JF_STATUS].lower()

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
            _validate_user_access,
            _validate_issue_urls,
            _set_issue,
            _set_facets,
            _persist
            ])
