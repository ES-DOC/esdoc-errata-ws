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

from errata.utils.exceptions import AuthenticationError
from errata.utils.exceptions import AuthorizationError



# Set of secured endpoints.
_SECURED_ENDPOINTS = {
    '/1/issue/close',
    '/1/issue/create',
    '/1/issue/update',
}

# GitHub API - user team membership within ES-DOC.
_GH_API_TEAMS = "https://api.github.com/orgs/ES-DOC/teams?access_token={}"

# Bare minimum required OAuth scopes.
_REQUIRED_OAUTH_SCOPES = {"read:org"}

# ESDOC GitHub team: errata-publication.
_ESDOC_GH_TEAM_ERRATA_PUBLICATION = 'errata-publication'


def _authenticate(oauth_token):
    """Authenticate request against github oauth teams api.

    """
    # Authenticate against GitHub API.
    url = _GH_API_TEAMS.format(oauth_token)
    r = requests.get(url, headers={'Accept': 'application/json'})
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


def secure_request(handler):
    """Enforces request level security policy (if necesaary).

    Policy is as follows:
    1.  Check if requested resource is in secured endpoints.
    2.  Authenticate against GitHub OAuth API.
    3.  Authorize against user's ES-DOC GitHub team membership.

    :param utils.http.HTTPRequestHandler handler: An HTTP request handler.
    :returns: Set of errata-publication teams that user is a member of.
    :rtype: set

    :raises: exceptions.AuthenticationError, exceptions.AuthorizationError

    """
    # Escape if not required.
    if not handler.request.path.split("?")[0] in _SECURED_ENDPOINTS:
        return

    # Extract user's GitHub OAuth personal access token from request.
    credentials = handler.request.headers['Authorization']
    credentials = credentials.replace('Basic ', '')
    credentials = base64.b64decode(credentials).split(':')
    oauth_token = credentials[1]

    return _authorize(_authenticate(oauth_token), _ESDOC_GH_TEAM_ERRATA_PUBLICATION)
