# -*- coding: utf-8 -*-

"""
.. module:: handlers.ops.credtest.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - Authentication and authorization test.

.. moduleauthor:: Atef Ben Nasser <abennasser@ipsl.fr>


"""
import tornado

import errata
from errata.utils.http import process_request
from errata.utils.http_security import apply_policy



# Query parameter names.
_PARAM_LOGIN = 'login'
_PARAM_TOKEN = 'token'
_PARAM_INSTITUTE = 'institute'


class VerifyAuthorizationRequestHandler(tornado.web.RequestHandler):
    """Operations heartbeat request handler.

    """
    def get(self):
        """HTTP GET handler.

        """
        def _verify():
            """Verifies user is authorized to manage an institute's errata.

            """
            apply_policy(
                self.get_argument(_PARAM_LOGIN),
                self.get_argument(_PARAM_TOKEN),
                self.get_argument(_PARAM_INSTITUTE)
                )


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                "message": "User allowed to manage errata for institute {}".format(self.get_argument(_PARAM_INSTITUTE))
            }


        # Process request.
        process_request(self, [
            _verify,
            _set_output
            ])
