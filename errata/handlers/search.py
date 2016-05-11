# -*- coding: utf-8 -*-

"""
.. module:: handlers.search.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - search issues endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from errata import db
from errata.utils.http import HTTPRequestHandler
from errata.utils import logger



# Query parameter names.
_PARAM_PROJECT = 'project'
_PARAM_SEVERITY = 'severity'
_PARAM_STATE = 'state'
_PARAM_TIMESTAMP = 'timestamp'
_PARAM_WORKFLOW = 'workflow'


class SearchRequestHandler(HTTPRequestHandler):
    """Search issue request handler.

    """
    def __init__(self, application, request, **kwargs):
        """Instance constructor.

        """
        super(SearchRequestHandler, self).__init__(application, request, **kwargs)

        self.issues = []
        self.project = None
        self.severity = None
        self.state = None
        self.timestamp = None
        self.total = 0
        self.workflow = None


    def get(self):
        """HTTP GET handler.

        """
        def _decode_request():
            """Decodes request.

            """
            if self.get_argument(_PARAM_PROJECT) != "*":
                logger.log_web("PARAM RECEIVED " + _PARAM_PROJECT)
                self.project = self.get_argument(_PARAM_PROJECT)

            if self.get_argument(_PARAM_SEVERITY) != "*":
                logger.log_web("PARAM RECEIVED " + _PARAM_SEVERITY)
                self.severity = self.get_argument(_PARAM_SEVERITY)

            if self.get_argument(_PARAM_STATE) != "*":
                logger.log_web("PARAM RECEIVED " + _PARAM_STATE)
                self.state = self.get_argument(_PARAM_STATE)

            if self.get_argument(_PARAM_TIMESTAMP) != "*":
                logger.log_web("PARAM RECEIVED " + _PARAM_TIMESTAMP)
                self.timestamp = self.get_argument(_PARAM_TIMESTAMP)

            if self.get_argument(_PARAM_WORKFLOW) != "*":
                logger.log_web("PARAM RECEIVED " + _PARAM_WORKFLOW)
                self.workflow = self.get_argument(_PARAM_WORKFLOW)


        def _set_data():
            """Pulls data from db.

            """
            with db.session.create():
                self.issues = db.dao.get_issues(
                    project=self.project,
                    state=self.state,
                    workflow=self.workflow,
                    severity=self.severity)
                self.total = db.utils.get_count(db.models.Issue)


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output_encoding = 'json'
            self.output = {
                'count': len(self.issues),
                'results': self.issues,
                'timestamp': self.timestamp,
                'total': self.total,
            }


        # Invoke tasks.
        self.invoke([], [
            _decode_request,
            _set_data,
            _set_output
            ])
