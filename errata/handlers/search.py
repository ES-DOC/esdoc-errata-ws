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
from errata.utils.http import HTTP_HEADER_Access_Control_Allow_Origin



# Query parameter names.
_PARAM_INSTITUTE = 'institute'
_PARAM_PROJECT = 'project'
_PARAM_SEVERITY = 'severity'
_PARAM_STATE = 'state'
_PARAM_TIMESTAMP = 'timestamp'
_PARAM_WORKFLOW = 'workflow'

# Query parameter validation schema.
_REQUEST_VALIDATION_SCHEMA = {
    _PARAM_INSTITUTE: {
        'required': True,
        'type': 'list', 'items': [{'type': 'string'}]
    },
    _PARAM_PROJECT: {
        'required': True,
        'type': 'list', 'items': [{'type': 'string'}]
    },
    _PARAM_SEVERITY: {
        'required': True,
        'type': 'list', 'items': [{'type': 'string'}]
    },
    _PARAM_STATE: {
        'required': True,
        'type': 'list', 'items': [{'type': 'string'}]
    },
    _PARAM_TIMESTAMP: {
        'required': True,
        'type': 'list', 'items': [{'type': 'string'}]
    },
    _PARAM_WORKFLOW: {
        'required': True,
        'type': 'list', 'items': [{'type': 'string'}]
    }
}


class SearchRequestHandler(HTTPRequestHandler):
    """Search issue request handler.

    """
    def __init__(self, application, request, **kwargs):
        """Instance constructor.

        """
        super(SearchRequestHandler, self).__init__(application, request, **kwargs)

        self.issues = []
        self.institute = None
        self.project = None
        self.severity = None
        self.state = None
        self.timestamp = None
        self.total = 0
        self.workflow = None


    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(HTTP_HEADER_Access_Control_Allow_Origin, "*")


    def get(self):
        """HTTP GET handler.

        """
        def _decode_request():
            """Decodes request.

            """
            self.timestamp = self.get_argument(_PARAM_TIMESTAMP)
            if self.get_argument(_PARAM_INSTITUTE) != "*":
                self.institute = self.get_argument(_PARAM_INSTITUTE)
            if self.get_argument(_PARAM_PROJECT) != "*":
                self.project = self.get_argument(_PARAM_PROJECT)
            if self.get_argument(_PARAM_SEVERITY) != "*":
                self.severity = self.get_argument(_PARAM_SEVERITY)
            if self.get_argument(_PARAM_STATE) != "*":
                self.state = self.get_argument(_PARAM_STATE)
            if self.get_argument(_PARAM_WORKFLOW) != "*":
                self.workflow = self.get_argument(_PARAM_WORKFLOW)


        def _set_data():
            """Pulls data from db.

            """
            with db.session.create():
                self.issues = db.dao.get_issues(
                    institute=self.institute,
                    project=self.project,
                    state=self.state,
                    workflow=self.workflow,
                    severity=self.severity
                    )
                self.total = db.utils.get_count(db.models.Issue)


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                'count': len(self.issues),
                'results': self.issues,
                'timestamp': self.timestamp,
                'total': self.total,
            }


        # Invoke tasks.
        self.invoke(_REQUEST_VALIDATION_SCHEMA, [
            _decode_request,
            _set_data,
            _set_output
            ])
