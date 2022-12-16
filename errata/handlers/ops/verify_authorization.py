import tornado

import errata
from errata.utils import config
from errata.utils.http import process_request
from errata.utils.http_security import apply_policy



# Query parameter names.
_PARAM_LOGIN = 'login'
_PARAM_TOKEN = 'token'
_PARAM_INSTITUTE = 'institute'
_PARAM_PROJECT = 'project'


class VerifyAuthorizationRequestHandler(tornado.web.RequestHandler):
    """Operations heartbeat request handler.

    """
    def get(self):
        """HTTP GET handler.

        """
        def _verify():
            """Verifies user is authorized to manage an institute's errata.

            """
            if config.apply_security_policy == True:
                apply_policy(
                    self.get_argument(_PARAM_LOGIN),
                    self.get_argument(_PARAM_TOKEN),
                    self.get_argument(_PARAM_PROJECT),
                    self.get_argument(_PARAM_INSTITUTE)
                    )


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                "message": "User allowed to manage errata: project={}; institute={}.".format(
                    self.get_argument(_PARAM_PROJECT), self.get_argument(_PARAM_INSTITUTE))
            }


        # Process request.
        process_request(self, [
            _verify,
            _set_output
            ])
