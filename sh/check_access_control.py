# -*- coding: utf-8 -*-

"""
.. module:: http_security.py
   :license: GPL/CeCIL
   :platform: Unix, Windows
   :synopsis: Asserts user access control.

.. moduleauthor:: Mark A. Conway-Greenslade


"""
import argparse
import json

import requests



# Define command line argument parser.
_ARGS = argparse.ArgumentParser("Enforces user access control.")
_ARGS.add_argument(
    "--oauth-token",
    help="A GitHub OAuth personal access token",
    dest="oauth_token",
    type=str
    )
_ARGS.add_argument(
    "--team",
    help="The team that the user wishes to have access to",
    dest="team",
    type=str
    )

# GitHub API - user team membership within ES-DOC.
_GH_API_TEAMS = "https://api.github.com/orgs/ES-DOC/teams?access_token={}"

# Bare minimum required OAuth scopes.
_REQUIRED_OAUTH_SCOPES = {"read:org"}


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


def _authenticate(oauth_token):
    """Authenticate request against github oauth api.

    """
    # Authenticate against GitHub API.
    url = _GH_API_TEAMS.format(oauth_token)
    r = requests.get(url, headers={
        'Accept': 'application/json'
        })
    if r.status_code != 200:
        raise AuthenticationError()

    # Verify required OAuth scopes.
    scopes = set(r.headers['X-OAuth-Scopes'].split(", "))
    if _REQUIRED_OAUTH_SCOPES - scopes:
        raise AuthenticationError()

    return set([i['name'] for i in json.loads(r.text)])


def _authorize(membership, team):
    """Authorizes access by confirming that a user is a member of appropriate team.

    """
    membership = [i for i in membership if i.startswith(team)]
    if not membership:
        raise AuthorizationError()

    return membership


# Main entry point.
if __name__ == '__main__':
    args = _ARGS.parse_args()
    print _authorize(_authenticate(args.oauth_token), args.team)
