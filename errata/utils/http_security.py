# -*- coding: utf-8 -*-
"""
.. module:: utils.misc.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Miscellaneous utility functions.

.. moduleauthor:: Guillaume Levavasseur <glipsl@ipsl.jussieu.fr>


"""
import base64
import json
import requests

from errata.utils import exceptions
from errata.utils import constants



# Set of secured endpoints.
_SECURED_ENDPOINTS = {
    '/1/issue/close',
    '/1/issue/create',
    '/1/issue/update',
}

# GitHub API - user team membership within ES-DOC.
_GH_API_TEAMS = "https://api.github.com/orgs/ES-DOC/teams?access_token={}"

# GitHub API - user team membership within GitHub.
_GH_API_USER = "https://api.github.com/user?access_token={}"

# Bare minimum required OAuth scopes.
_REQUIRED_OAUTH_SCOPES = {"read:org"}


def _authenticate(gh_login, oauth_token):
    """Authenticate request against github oauth teams api.

    """
    # Authenticate against GitHub user API.
    url = _GH_API_USER.format(oauth_token)
    r = requests.get(url, headers={'Accept': 'application/json'})
    if r.status_code != 200:
        raise exceptions.AuthenticationError()

    # Verify that GH login & token map to same GH account.
    user = json.loads(r.text)
    if gh_login != user['login']:
        raise exceptions.AuthenticationError()

    # Return minimal user information.
    return user['name'] or gh_login


def _authorize(oauth_token, team):
    """Authorizes access by confirming that a user is a member of appropriate team.

    """
    # Authorize against GitHub organization team API.
    url = _GH_API_TEAMS.format(oauth_token)
    r = requests.get(url, headers={'Accept': 'application/json'})
    if r.status_code != 200:
        raise exceptions.AuthorizationError()

    # Verify minimal OAuth scope(s).
    scopes = set(r.headers['X-OAuth-Scopes'].split(", "))
    if _REQUIRED_OAUTH_SCOPES - scopes:
        raise exceptions.AuthorizationError()

    # Verify team membership.
    teams = set([i['name'] for i in json.loads(r.text)])
    teams = [i for i in teams if i.startswith(team)]
    if not teams:
        raise exceptions.AuthorizationError()

    # Return team membership.
    return teams


def secure_request(handler):
    """Enforces request level security policy (if necesaary).

    :param utils.http.HTTPRequestHandler handler: An HTTP request handler.

    :raises: exceptions.AuthenticationError, exceptions.AuthorizationError

    """
    # Escape if not required.
    if not handler.request.path.split("?")[0] in _SECURED_ENDPOINTS:
        return

    # Extract user's GitHub OAuth personal access token from request.
    credentials = handler.request.headers['Authorization']
    credentials = credentials.replace('Basic ', '')
    credentials = base64.b64decode(credentials).split(':')
    gh_login, oauth_token = credentials

    # Authenticate.
    handler.user_name = _authenticate(gh_login, oauth_token)

    # Authorize.
    handler.user_teams = _authorize(oauth_token, constants.ERRATA_GH_TEAM)
