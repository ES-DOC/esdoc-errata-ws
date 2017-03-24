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
            if config.mode == "dev" and config.network_state == "down":
                return

            urls = traverse([self.request.data.get((i)) for i in [JF_URL, JF_MATERIALS]])
            for url in urls:
                if url != '':
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
            issue.institution_id = obj[JF_INSTITUTE].lower()
            issue.materials = ",".join(obj.get(JF_MATERIALS, []))
            issue.mip_era = obj[JF_PROJECT].lower()
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
            # Initialise facets.
            self.facets = []

            # Iterate facet types:
            for ft in [i for i in constants.FACET_TYPE if FACET_TYPE_JSON_FIELD[i] in self.request.data]:
                # ... set facet values.
                fv_list = self.request.data[FACET_TYPE_JSON_FIELD[ft]]
                if not isinstance(fv_list, list):
                    fv_list = [fv_list]
                fv_list = [i for i in fv_list if i and len(i.strip()) > 0]

                # ... set facets.
                for fv in set(fv_list):
                    f = db.models.IssueFacet()
                    f.facet_value = fv.strip()
                    f.facet_type = ft
                    f.issue_uid = self.issue.uid
                    self.facets.append(f)


        def _set_pid_tasks():
            """Persists pid handles.

            """
            self.pid_tasks = []
            for dset_id in self.request.data[JF_DATASETS]:
                task = db.models.PIDServiceTask()
                task.action = constants.PID_ACTION_INSERT
                task.issue_uid = self.issue.uid
                task.dataset_id = dset_id
                self.pid_tasks.append(task)


        def _persist():
            """Persists data to dB.

            """
            db.session.insert(self.issue)
            for facet in self.facets:
                db.session.insert(facet)
            for pid_task in self.pid_tasks:
                db.session.insert(pid_task)


        # Process request.
        with db.session.create(commitable=True):
            process_request(self, [
                _validate_user_access,
                _validate_issue_urls,
                _set_issue,
                _set_facets,
                _set_pid_tasks,
                _persist
                ])
