# -*- coding: utf-8 -*-

"""
.. module:: http_security.py
   :license: GPL/CeCIL
   :platform: Unix, Windows
   :synopsis: Asserts user access control.

.. moduleauthor:: Mark A. Conway-Greenslade


"""
import argparse

from pyesdoc.security import is_authenticated_user
from pyesdoc.security import is_team_member



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


class AuthenticationError(Exception):
    """Raised when an authentication assertion fails.

    """
    def __init__(self):
        """Instance constructor.

        """
        super(AuthenticationError, self).__init__("SECURITY EXCEPTION :: AUTHENTICATION FAILURE")
        self.response_code = 401


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
    if not is_authenticated_user(user_id, access_token):
        raise AuthenticationError()

    return user_id


def _authorize(user_id, team_id):
    """Authorizes access by confirming that a user is a member of appropriate team.

    """
    if not is_team_member(team_id, user_id):
        raise AuthorizationError()

    return 'Authenticated user {} is an authorized member of the {} team'.format(user_id, team_id)


# Main entry point.
if __name__ == '__main__':
    args = _ARGS.parse_args()
    print _authorize(_authenticate(args.user_id, args.access_token), args.team)
