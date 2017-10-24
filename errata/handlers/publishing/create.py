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
from errata.utils import exceptions
from errata.utils.constants_json import *
from errata.utils.http import process_request
from errata.utils.misc import traverse
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
        def _validate_project():
            """Validates project is supported.

            """
            self.project = self.request.data[JF_PROJECT]
            self.project_conf = config_esg.get_active_project(self.project)
            if self.project_conf is None:
                raise exceptions.UnknownProjectError(self.project)


        def _validate_issue_facets():
            """Validates facets associated with incoming issue.

            """
            # Assert: facets are supported.
            for facet_type in self.request.data[JF_FACETS]:
                if facet_type not in self.project_conf['facets']:
                    raise exceptions.UnknownFacetError(self.project, facet_type)

            # Assert: facet values are valid.
            for facet_type, facet_values in self.request.data[JF_FACETS].items():
                facet_conf = self.project_conf['facets'][facet_type]
                collection_namespace = facet_conf['collection'].namespace
                for facet_value in facet_values:
                    facet_namespace = '{}:{}'.format(collection_namespace, facet_value)
                    if pyessv.parse_namespace(facet_namespace, strictness=3) is None:
                        raise exceptions.InvalidFacetError(self.project, facet_type, facet_value)


        def _validate_issue_urls():
            """Validates URL's associated with incoming request.

            """
            if config.apply_security_policy:
                urls = [self.request.data.get(i) for i in [JF_URL, JF_MATERIALS]]
                for url in traverse(urls):
                    validate_url(url)


        def _set_issue():
            """Creates issue.

            """
            obj = self.request.data

            # ... core info;
            self.issue = issue = db.models.Issue()
            issue.description = obj[JF_DESCRIPTION].strip()
            issue.institute = obj[JF_INSTITUTE].lower()
            issue.materials = ",".join(obj.get(JF_MATERIALS, []))
            issue.project = obj[JF_PROJECT].lower()
            issue.severity = obj[JF_SEVERITY].lower()
            issue.title = obj[JF_TITLE].strip()
            issue.uid = obj[JF_UID].strip()
            issue.url = obj.get(JF_URL)
            issue.status = obj[JF_STATUS].lower()

            # ... tracking info;
            issue.date_closed = obj.get(JF_DATE_CLOSED)
            issue.date_created = obj[JF_DATE_CREATED]
            issue.date_updated = obj.get(JF_DATE_UPDATED, issue.date_created)
            issue.closed_by = self.user_id if issue.date_closed else None
            issue.created_by = self.user_id
            issue.updated_by = self.user_id if issue.date_updated else None


        def _set_facets():
            """Sets search facets to be persisted to database.

            """
            self.facets = facets = []
            for facet_type, facet_values in self.request.data[JF_FACETS].items():
                for facet_value in set(facet_values):
                    facet = db.models.IssueFacet()
                    facet.facet_type = facet_type
                    facet.facet_value = facet_value.strip()
                    facet.issue_uid = self.issue.uid
                    facets.append(facet)


        def _set_pid_tasks():
            """Persists pid handles.

            """
            self.pid_tasks = []
            if self.project_conf['is_pid_client']:
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
                _validate_project,
                _validate_issue_facets,
                _validate_issue_urls,
                _set_issue,
                _set_facets,
                _set_pid_tasks,
                _persist
            ])
