# -*- coding: utf-8 -*-

"""
.. module:: handlers.hs_handler.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - handle service search endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
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


def _get_errata_information(pid):
    """Returns formatted errata information from handle service.

    Handle service returns a dictionary of dictionaries.

    Structure = {
        handle_1 : {Queried/Predecessors/Successors_handles : Issue ...},
        handle_2 : {Queried/Predecessors/Successors_handles : Issue ...},
        ... etc
        }

    """
    data, _, _, _, _ = harvest_errata_information(pid)

    return pid, sorted(data.values(), key=lambda i: i[3])


class HandleServiceRequestHandler(HTTPRequestHandler):
    """Retrieve issue request handler.

    """
    def __init__(self, application, request, **kwargs):
        """Instance constructor.

        """
        super(HandleServiceRequestHandler, self).__init__(application, request, **kwargs)

        self.handles = []
        self.errata = []
        self.timestamp = None


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
            for pid in self.handles:
                self.errata.append(_get_errata_information(pid))


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                'errata': self.errata,
                'timestamp': self.timestamp
            }


        # Invoke tasks.
        self.invoke(_REQUEST_VALIDATION_SCHEMA, [
            _decode_request,
            _invoke_pid_handle_service,
            _set_output
            ])
