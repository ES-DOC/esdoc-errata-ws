# -*- coding: utf-8 -*-

"""
.. module:: handlers.ops.credtest.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - Authentication and authorization test.

.. moduleauthor:: Atef Ben Nasser <abennasser@ipsl.fr>


"""
import tornado

from errata.utils import constants
from errata.utils import exceptions
from errata.utils.http import process_request


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
        print 111, self.get_argument(_PARAM_LOGIN), self.get_argument(_PARAM_TOKEN), self.get_argument(_PARAM_INSTITUTE)


        def _validate_user_access():
            """Validates user's institutional access rights.

            """
            return
            # # Super & insitutional users have access.
            # for team in sorted(self.user_teams):
            #     if team == constants.ERRATA_GH_TEAM:
            #         return
            #     if team.split("-")[-1] == self.team:
            #         return

            # # User has no access rights to this particular issue.
            # raise exceptions.AuthorizationError()


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                "message": "User allowed to post issues related to institute {}".format(self.team),
                "code": 200
            }


        # Process request.
        process_request(self, [
                        _validate_user_access,
                        _set_output
                        ])
