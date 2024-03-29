import tornado

from errata_ws.handle_service.harvest import harvest_errata_information
from errata_ws.utils import constants
from errata_ws.utils.http import process_request
from errata_ws.handle_service.utils import resolve_input



# Query parameter names.
_PARAM_PIDS = 'pids'


def _get_errata_information(pid):
    """Returns formatted errata information from handle service.

    Handle service returns a dictionary of dictionaries.

    Structure = {
        handle_1 : {Queried/Predecessors/Successors_handles : Issue ...},
        handle_2 : {Queried/Predecessors/Successors_handles : Issue ...},
        ... etc
        }

    """
    pid = resolve_input(pid)
    data, incomplete_search = harvest_errata_information(pid)
    ordered_data = sorted(data.values(), key=lambda i: i[3])
    ordered_data[0][4] = 1
    ordered_data[-1][5] = 1
    return pid, ordered_data, incomplete_search


class ResolvePIDRequestHandler(tornado.web.RequestHandler):
    """Retrieve PID's request handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(constants.HTTP_HEADER_Access_Control_Allow_Origin, "*")


    def get(self):
        """HTTP GET handler.

        """
        def _invoke_pid_handle_service():
            """Invoke remote PID handle service.

            """
            self.errata = [_get_errata_information(i) for i in self.get_argument(_PARAM_PIDS).split(",")]


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                'errata': self.errata
            }


        # Process request.
        process_request(self, [
            _invoke_pid_handle_service,
            _set_output
            ])
