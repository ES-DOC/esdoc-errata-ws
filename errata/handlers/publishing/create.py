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
import os

from errata import db
from errata.utils import config as cf
from errata.utils.config import _get_facet_config, _get_remote_config
from errata.utils import constants
from errata.utils import exceptions
from errata.utils import logger
from errata.utils.constants_json import *
from errata.utils.http import process_request
from errata.utils.misc import traverse
from errata.utils.validation import validate_url
from ESGConfigParser import SectionParser
from ESGConfigParser.exceptions import NoConfigOptions


class CreateIssueRequestHandler(tornado.web.RequestHandler):
    """issue handler.

    """
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "content-type, Authorization")
        self.set_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.set_header('Access-Control-Allow-Credentials', True)

    def options(self):

        self.set_status(204)
        self.finish()

    def post(self):

        """HTTP POST handler.

        """
        def _validate_user_access():
            """Validates user's institutional access rights.

            """
            print('here')
            print(self.request.data[JF_FACETS])
            # Super & institutional users have access.
            for team in sorted(self.user_teams):
                if team == constants.ERRATA_GH_TEAM:
                    return
                if team.split("-")[-1] == self.request.data[JF_FACETS][JF_INSTITUTE][0].lower():
                    return

            # User has no access rights to this particular issue.
            raise exceptions.AuthorizationError()

        def _validate_facets():
            """
            Validates facets using project's appropriate ini file and translates facet types to universal approximate.
            :return:
            """
            config = _get_remote_config(self.request.data[JF_PROJECT])
            project = self.request.data[JF_PROJECT]
            self.project_conf = _get_facet_config(project)
            logger.log_web('Validating received facets...')
            self.facets_dict = dict()
            data_facets = self.request.data[JF_FACETS]
            config = SectionParser(os.path.join(os.environ.get('ERRATA_WS_HOME'), 'ops/config/'), 'project:' + project)
            logger.log_web('iterating over facets')
            print(data_facets)
            for facet_type, facet_value in data_facets.iteritems():
                facet_type = str(facet_type)
                try:
                    for fv in facet_value:
                        print(fv)
                        if facet_type.lower() not in ['project', 'mip_era'] and type(
                                config.get_options(facet_type)[0]) != re._pattern_type:
                            if fv.lower() not in [x.lower() for x in config.get_options(facet_type)[0]]:
                                logger.log_web_error('Facet {} not recognized with value {}...'.format(facet_type, fv))
                                raise exceptions.RequestValidationException(
                                    'Facet {} not recognized with value {}...'.format(facet_type, fv))
                        elif facet_type.lower() not in ['project', 'mip_era']:
                            if not re.match(config.get_options(facet_type)[0], fv):
                                logger.log_web_error(
                                    '{} didnt match the regex string {}'.format(config.get_options(facet_type)[0]))
                                raise exceptions.RequestValidationException(
                                    '{} didnt match the regex string {}'.format(config.get_options(facet_type)[0]))
                except NoConfigOptions as nco:
                    raise exceptions.RequestValidationException('Facet type {} not recognized'.format(facet_type))

                if facet_type in self.project_conf.keys() and facet_type in data_facets.keys():
                    if self.project_conf[facet_type] not in self.facets_dict.keys():
                        self.facets_dict[self.project_conf[facet_type].lower()] = facet_value
                    else:
                        self.facets_dict[self.project_conf[facet_type].lower()].append(facet_value)
                elif facet_type in data_facets.keys():
                    self.facets_dict[facet_type.lower()] = facet_value
            logger.log_web('Facets successfully validated.')
            if 'mip_era' in self.facets_dict.keys():
                self.facets_dict[JF_PROJECT] = self.request.data[JF_FACETS]['mip_era']

        def _validate_issue_urls():
            """Validates URL's associated with incoming request.

            """
            if cf.mode == "dev" and cf.network_state == "down":
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
            facets = self.facets_dict
            issue.date_closed = obj.get(JF_DATE_CLOSED)
            issue.date_created = obj[JF_DATE_CREATED]
            issue.created_by = self.user_name
            issue.description = obj[JF_DESCRIPTION]
            # TODO workaround till further discussed.
            if JF_INSTITUTE in facets.keys():
                issue.institute = facets[JF_INSTITUTE][0].lower()
            elif JF_SECTOR in facets.keys() or JF_WORK_PACKAGE in facets.keys():
                issue.institute = ''
            issue.materials = ",".join(facets.get(JF_MATERIALS, []))
            # issue.project = facets[JF_PROJECT][0].lower()
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
            # Initialise facets.
            self.facets = []
            # Iterate facet types:
            for ft in [i for i in constants.FACET_TYPE if FACET_TYPE_JSON_FIELD[i] in self.request.data or
                            FACET_TYPE_JSON_FIELD[i] in self.facets_dict.keys()]:
                # ... set facet values.
                if FACET_TYPE_JSON_FIELD[ft] in self.request.data.keys():
                    fv_list = self.request.data[FACET_TYPE_JSON_FIELD[ft]]
                else:
                    fv_list = self.facets_dict[FACET_TYPE_JSON_FIELD[ft]]

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
            if constants[self.request.data[JF_PROJECT].lower()]:
                self.pid_tasks = []
                for dset_id in self.request.data[JF_DATASETS]:
                    task = db.models.PIDServiceTask()
                    task.action = constants.PID_ACTION_INSERT
                    task.issue_uid = self.issue.uid
                    task.dataset_id = dset_id
                    self.pid_tasks.append(task)
            else:
                logger.log_web('Project doesnt have PID support, skipping pid insertion...')

        def _persist():
            """Persists data to dB.

            """
            db.session.insert(self.issue)
            for facet in self.facets:
                db.session.insert(facet)
            if self.project_conf['pid']:
                for pid_task in self.pid_tasks:
                    db.session.insert(pid_task)

        # Process request.
        with db.session.create(commitable=True):
            process_request(self, [
                _validate_user_access,
                _validate_facets,
                _validate_issue_urls,
                _set_issue,
                _set_facets,
                _set_pid_tasks,
                _persist
            ])
