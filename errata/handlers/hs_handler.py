# -*- coding: utf-8 -*-

"""
.. module:: handlers.hs_handler.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - handle service search endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import collections

from errata import db
from errata.handle_service.harvest import harvest_errata_information
from errata.utils.http import HTTPRequestHandler
from errata.utils.http import HTTP_HEADER_Access_Control_Allow_Origin



# Query parameter names.
_PARAM_HANDLES = 'handles'
_PARAM_TIMESTAMP = 'timestamp'

# Query parameter validation schema.
_REQUEST_VALIDATION_SCHEMA = {
    _PARAM_HANDLES: {
        'required': True,
        'type': 'list', 'schema': {'type': 'string'}
    },
    _PARAM_TIMESTAMP: {
        'required': True,
        'type': 'list', 'items': [{'type': 'string'}]
    }
}


def _get_errata_information(handle):
    """Returns formatted errata information from handle service.

    Handle service returns a dictionary of dictionaries.

    Structure = {
        handle_1 : {Queried/Predecessors/Successors_handles : Issue ...},
        handle_2 : {Queried/Predecessors/Successors_handles : Issue ...},
        ... etc
        }

    """
    result = harvest_errata_information(handle)
    data = [(k, v[0], v[1], v[2]) for k, v in result[0].iteritems()]
    id = result[1]
    is_latest = result[2]
    has_issues = result[3]
    incomplete_retracing = result[4]

    return sorted(data, key=lambda i: i[2]), id, is_latest, has_issues, incomplete_retracing


class HandleServiceRequestHandler(HTTPRequestHandler):
    """Retrieve issue request handler.

    """
    def __init__(self, application, request, **kwargs):
        """Instance constructor.

        """
        super(HandleServiceRequestHandler, self).__init__(application, request, **kwargs)

        self.handles = []
        self.uid_list = dict()
        self.data = []
        self.errata = []
        self.timestamp = None
        self.has_issue = None
        self.latest = None
        self.incomplete_retracing = None
        self.id = None


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
            self.handles = self.get_argument(_PARAM_HANDLES).split(",")

        def _invoke_pid_handle_service():
            """Invoke remote PID handle service.

            """
            for handle in self.handles:
                errata_info = _get_errata_information(handle)
                self.errata.append([errata_info[1], errata_info[0]])
                self.id = errata_info[1]
                self.is_latest = errata_info[2]
                self.has_issue = errata_info[3]
                self.incomplete_retracing = errata_info[4]


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output_encoding = 'json'
            self.output = {
                'errata': sorted(self.errata, key=lambda i: i[0]),
                'has_issue': self.has_issue,
                'latest': self.is_latest,
                'incomplete_retracing': self.incomplete_retracing,
                'timestamp': self.timestamp
            }


        # Invoke tasks.
        self.invoke(_REQUEST_VALIDATION_SCHEMA, [
            _decode_request,
            _invoke_pid_handle_service,
            _set_output
            ])
