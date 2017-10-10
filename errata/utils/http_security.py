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

from pyesdoc.security import AuthenticationError
from pyesdoc.security import AuthorizationError
from pyesdoc.security import is_authenticated_user
from pyesdoc.security import is_team_member
from pyesdoc.security import strip_credentials

from errata.utils import config
from errata.utils import constants



# GitHub identifier of errata-publication team.
_GH_TEAM_ID = 2375691

# Set of whitelisted endpoints.
_WHITELISTED_ENDPOINTS = {
    '/',
    '/verify-authorization',
    '/1/issue/retrieve',
    '/1/issue/retrieve-all',
    '/1/issue/search',
    '/1/issue/search-setup',
    '/1/pid-queue/search',
    '/1/resolve/issue',
    '/1/resolve/pid',
    '/1/resolve/simple-pid'
}


def authenticate(credentials):
    """Authenticates user credentials request against GitHub user api.

    :param tuple credentials: 2 member tuple (GitHub username, GitHub access token)

    :returns: GitHub username
    :rtype: str

    """
    user_id, access_token = credentials
    if not is_authenticated_user(user_id, access_token):
        raise AuthenticationError()

    return user_id


def authorize(user_id):
    """Authorizes user against GitHub team membership api.

    :param str user_id: GitHub username.

    """
    if not is_team_member(_GH_TEAM_ID, user_id):
        raise AuthorizationError()
    # TODO verify institute


def secure_request(handler):
    """Enforces request level security policy (if necessary).

    :param utils.http.HTTPRequestHandler handler: An HTTP request handler.

    :raises: AuthenticationError, AuthorizationError

    """
    if config.apply_security_policy == False or \
       handler.request.path in _WHITELISTED_ENDPOINTS:
        handler.user_id = "tester"
        handler.user_teams = [constants.ERRATA_GH_TEAM]
        return

    credentials = _strip_credentials(handler.request.headers['Authorization'])

    # Authenticate.
    handler.user_id, _ = _authenticate(credentials)

    # Authorize.
    handler.user_teams = _authorize(oauth_token, constants.ERRATA_GH_TEAM)
