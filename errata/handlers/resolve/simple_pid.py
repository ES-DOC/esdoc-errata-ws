import tornado

from errata.handle_service.harvest import harvest_simple_errata
from errata.utils import constants
from errata.utils.http import process_request
from errata.handle_service.utils import resolve_input


# Query parameter names.
_PARAM_DATASETS = 'datasets'


def _get_simple_errata_information(user_input):
    """Returns formatted simple errata information from handle service.
    """
    data = [user_input, None, None, None, None, False]
    pid = resolve_input(user_input)
    if pid is not None:
        data = harvest_simple_errata(pid)
    return data


class ResolveSimplePIDRequestHandler(tornado.web.RequestHandler):
    """Retrieve PID's request handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(constants.HTTP_HEADER_Access_Control_Allow_Origin, "*")

    def get(self):
        """HTTP GET handler.

        """
        def _get_pid_info():
            """Invoke remote PID handle service.

            """
            self.data = [_get_simple_errata_information(i) for i in self.get_argument(_PARAM_DATASETS).split(",")]

        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = dict()
            for e in self.data:
                self.output[e[0]] = {
                                    'drs': e[1],
                                    'version': e[2],
                                    'errata_ids': e[3],
                                    'has_errata': e[4],
                                    'success': e[5]
                                    }

        # Process request.
        process_request(self, [
            _get_pid_info,
            _set_output
            ])
