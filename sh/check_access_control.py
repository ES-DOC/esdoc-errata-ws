# -*- coding: utf-8 -*-

"""
.. module:: http_security.py
   :license: GPL/CeCIL
   :platform: Unix, Windows
   :synopsis: Asserts user access control.

.. moduleauthor:: Mark A. Conway-Greenslade


"""
import argparse

from errata.utils import security



# Define command line argument parser.
_ARGS = argparse.ArgumentParser("Checks user access control.")
_ARGS.add_argument(
    "--user",
    help="A GitHub OAuth user login",
    dest="user_id",
    type=str
    )
_ARGS.add_argument(
    "--access-token",
    help="A GitHub OAuth personal access token",
    dest="access_token",
    type=str
    )
_ARGS.add_argument(
    "--team",
    help="The team that the user wishes to have access to",
    dest="team",
    type=str
    )


class AuthorizationError(Exception):
    """Raised when an authorization assertion fails.

    """
    def __init__(self):
        """Instance constructor.

        """
        super(AuthorizationError, self).__init__("SECURITY EXCEPTION :: AUTHORIZATION FAILURE")
        self.response_code = 403


def _authenticate(user_id, access_token):
    """Authenticate request against github oauth api.

    """
    return security.authenticate_user((user_id, access_token))


def _authorize(user_id, team_id):
    """Authorizes access by confirming that a user is a member of appropriate team.

    """
    security.authorize_user(team_id, user_id)


# Main entry point.
if __name__ == '__main__':
    args = _ARGS.parse_args()
    _authorize(_authenticate(args.user_id, args.access_token), args.team)
