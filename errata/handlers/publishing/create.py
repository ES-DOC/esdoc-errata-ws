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
from errata.utils import config
from errata.utils import constants
from errata.utils import exceptions
from errata.utils.constants_json import *
from errata.utils.http import process_request
from errata.utils.misc import traverse
from errata.utils.validation import validate_url
from errata.utils.pid_connector import create_connector, add_errata_to_handle


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
            if config.mode == "dev" and config.network_state == "down":
                return

            urls = traverse([self.request.data.get((i)) for i in [JF_URL, JF_MATERIALS]])
            for url in urls:
                validate_url(url)


        def _set_issue():
            """Creates issue.

            """
            self.issue = issue = db.models.Issue()
            obj = self.request.data
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
            obj = self.request.data
            for facet_type in constants.FACET_TYPE:
                # Set facet values.
                if facet_type in obj and facet_type not in constants.MULTIPLE_FACETS:
                    facet_values = [obj[facet_type]]
                elif facet_type in constants.MULTIPLE_FACETS:
                    facet_values = obj.get('{}'.format(facet_type), [])

                else:
                    facet_values = obj.get('{}s'.format(facet_type), [])
                facet_values = [i for i in facet_values if i and len(i) > 0]
                # Set facets to be persisted.
                for facet_value in set(facet_values):
                    facet = db.models.IssueFacet()
                    facet.facet_value = facet_value
                    facet.facet_type = facet_type
                    facet.issue_uid = self.issue.uid
                    facets.append(facet)


        def _persist():
            """Persists data to dB.

            """
            # Persist issue.
            db.session.insert(self.issue)

            # Persist facets.
            for facet in self.facets:
                db.session.insert(facet)

        def _update_pid():
            """
            updates pid handles.

            """
            # Retrieving issue uid and affected dataset list.
            obj = self.request.data
            if constants.DATASETS in obj and constants.UID in obj:
                datasets = obj[constants.DATASETS]
                uid = obj[constants.UID]
            # Creating connection to pid server and updating handles one by one.
            connector = create_connector()
            connector.start_messaging_thread()
            for dataset in datasets:
                add_errata_to_handle(dataset, [uid], connector)
            connector.finish_messaging_thread()

        # Process request.
        with db.session.create(commitable=True):
            process_request(self, [
                _validate_user_access,
                _validate_issue_urls,
                _set_issue,
                _set_facets,
                _persist,
                _update_pid
                ])
