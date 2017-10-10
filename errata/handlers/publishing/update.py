# -*- coding: utf-8 -*-

"""
.. module:: handlers.update.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - update issue endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import difflib
import os
import tornado
import re

from errata import db

from errata.db.dao import get_issue
from errata.db.dao import get_issue_facets
from errata.db.dao import delete_facets
from errata.utils import constants
from errata.utils import logger
from errata.utils import exceptions
from errata.utils.constants_json import *
from errata.utils.http import process_request
from errata.utils.config import _get_facet_config, _get_remote_config
from ESGConfigParser import SectionParser
from ESGConfigParser.exceptions import NoConfigOptions


class UpdateIssueRequestHandler(tornado.web.RequestHandler):
    """issue handler.

    """

    def post(self):
        """HTTP POST handler.

        """

        def _validate_issue_exists():
            """Validates that the issue has been previously posted to the web-service.

            """
            issue = self.issue = get_issue(self.request.data[JF_UID])
            if issue is None:
                raise exceptions.UnknownIssueError(self.request.data[JF_UID])

        def _validate_user_access():
            """Validates user's institutional access rights.

            """
            # Super & insitutional users have access.
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
            for facet_type, facet_value in data_facets.iteritems():
                facet_type = str(facet_type)
                try:
                    for fv in facet_value:
                        if facet_type.lower() not in ['project', 'mip_era'] and \
                                type(config.get_options(facet_type)[0]) != re._pattern_type:
                            if fv.lower() not in [x.lower() for x in config.get_options(facet_type)[0]]:
                                logger.log_web_error('Facet {} not recognized with value {}.'
                                                     .format(facet_type, fv))
                                raise exceptions.RequestValidationException('Facet {} not recognized with value {}.'
                                                                            .format(facet_type, fv))
                        elif facet_type.lower() not in ['project', 'mip_era']:
                            if not re.match(config.get_options(facet_type)[0], fv):
                                logger.log_web_error(
                                    '{} didnt match the regex string {}'.format(config.get_options(facet_type)[0]))
                                raise exceptions.RequestValidationException('{} didnt match the regex string {}'
                                                                            .format(config.get_options(facet_type)[0]))
                except NoConfigOptions as nco:
                    pass

                if facet_type in self.project_conf.keys() and facet_type in data_facets.keys():
                    if self.project_conf[facet_type] not in self.facets_dict.keys():
                        self.facets_dict[self.project_conf[facet_type].lower()] = facet_value
                    else:
                        self.facets_dict[self.project_conf[facet_type].lower()].append(facet_value)
                elif facet_type in data_facets.keys():
                    self.facets_dict[facet_type.lower()] = facet_value
            logger.log_web('Facets successfully validated.')

        def _validate_issue_immutable_attributes():
            """Validates that issue attribute deemed to be immutable have not been changed.

            """
            for attr_name in constants.IMMUTABLE_ISSUE_ATTRIBUTES:
                if unicode(self.request.data[attr_name]).lower() != unicode(getattr(self.issue, attr_name)).lower():
                    raise exceptions.ImmutableIssueAttributeError(attr_name)
            logger.log_web('finished processing attributes...')
            logger.log_web('processing facets')
            for facet_name in constants.IMMUTABLE_ISSUE_FACETS:
                for facet_elt in self.request.data[JF_FACETS][facet_name]:
                    if unicode(facet_elt).lower() != unicode(getattr(self.issue, facet_name)).lower():
                        raise exceptions.ImmutableIssueAttributeError(facet_name)
            logger.log_web('Finished immutability test')

        def _validate_issue_description_change_ratio():
            """Validates that the degree of change in the issue's description is less than allowed ratio.

            """
            # Escape if no change.
            if self.request.data[JF_DESCRIPTION] == self.issue.description:
                return

            # Determine change ratio.
            diff = difflib.SequenceMatcher(None, self.issue.description, self.request.data[JF_DESCRIPTION])
            diff_ratio = 100 - round(diff.ratio(), 3) * 100
            if diff_ratio > constants.DESCRIPTION_CHANGE_RATIO:
                raise exceptions.IssueDescriptionChangeRatioError(diff_ratio)

        def _validate_issue_status():
            """Validates that issue status allows it to be updated.

            """
            if self.issue.status != constants.STATUS_NEW and \
                            self.request.data[JF_STATUS] == constants.STATUS_NEW:
                raise exceptions.InvalidIssueStatusError()

        def _persist_pid_tasks():
            """Persists pid handles.

            """
            if self.project_conf['pid']:
                # Set existing datasets.
                dsets_existing = get_issue_facets(self.issue.uid, constants.FACET_TYPE_DATASET)
                dsets_existing = set([i.facet_value for i in dsets_existing])

                # Set actual datasets.
                dsets_actual = set(self.request.data[JF_DATASETS])

                # Remove obsolete PID handle errata.
                for action, dsets in (
                        (constants.PID_ACTION_DELETE, list(dsets_existing - dsets_actual)),
                        (constants.PID_ACTION_INSERT, list(dsets_actual - dsets_existing)),
                ):
                    for dset in dsets:
                        task = db.models.PIDServiceTask()
                        task.action = action
                        task.issue_uid = self.issue.uid
                        task.dataset_id = dset
                        db.session.insert(task, False)
            else:
                logger.log_web("This project doesnt have PID support, skipping PID insertion...")

        def _persist_issue():
            """Persists issue update.

            """
            obj = self.request.data
            issue = self.issue
            issue.date_closed = obj.get(JF_DATE_CLOSED)
            issue.description = obj[JF_DESCRIPTION]
            issue.materials = ",".join(obj.get(JF_MATERIALS, []))
            issue.severity = obj[JF_SEVERITY].lower()
            issue.title = obj[JF_TITLE]
            issue.date_updated = obj[JF_DATE_UPDATED]
            issue.updated_by = self.user_name
            issue.url = obj.get(JF_URL)
            issue.status = obj[JF_STATUS].lower()

        def _persist_facets():
            """Insert new facets.

            """
            # Reset existing.
            delete_facets(self.issue.uid)

            self.facets = []
            # Iterate facet types:
            for ft in [i for i in constants.FACET_TYPE if FACET_TYPE_JSON_FIELD[i] in self.request.data or
                            FACET_TYPE_JSON_FIELD[i] in self.facets_dict.keys()]:
                # ... set facet values.
                logger.log_web('now setting facet type {}'.format(ft))
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
                    db.session.insert(f, False)

        # Process request.
        with db.session.create(commitable=True):
            process_request(self, [
                _validate_issue_exists,
                _validate_user_access,
                _validate_facets,
                _validate_issue_immutable_attributes,
                _validate_issue_description_change_ratio,
                _validate_issue_status,
                _persist_pid_tasks,
                _persist_issue,
                _persist_facets
            ])
