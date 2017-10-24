# -*- coding: utf-8 -*-
"""
.. module:: utils.misc.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Miscellaneous utility functions.

.. moduleauthor:: Guillaume Levavasseur <glipsl@ipsl.jussieu.fr>


"""
import json

import pyesdoc

from errata.utils import config
from errata.utils import constants



# GitHub team name.
_GH_TEAM = 'errata-publication'

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
    return pyesdoc.authenticate_user(credentials)


def authorize(user_id, institute_id):
    """Authorizes user against GitHub team membership api.

    :param str user_id: GitHub username.
    :param str institute_id: Institute identifier, e.g. ipsl.

    """
    pyesdoc.authorize_user(_GH_TEAM, user_id)
    pyesdoc.authorize_user('staff-{}'.format(institute_id), user_id)


def apply_policy(user_id, access_token, institute_id):
    """Applies security policy.

    :param str user_id: GitHub username.
    :param str access_token: GitHub access token.
    :param str institute_id: Institute identifier, e.g. ipsl.

    """
    authorize(authenticate((user_id, access_token)), institute_id)


def secure_request(handler):
    """Enforces request level security policy (if necessary).

    :param utils.http.HTTPRequestHandler handler: An HTTP request handler.

    """
    if config.apply_security_policy == False or \
       handler.request.path in _WHITELISTED_ENDPOINTS:
        handler.user_id = "tester"
        handler.user_teams = [constants.ERRATA_GH_TEAM]
        return

    # Authenticate.
    credentials = pyesdoc.strip_credentials(handler.request.headers['Authorization'])
    user_id = authenticate(credentials)

    # Authorize.
    # shandler.user_teams = authorize(user_id, constants.ERRATA_GH_TEAM)

    # Authorize (via institute identifier).
    issue = json.loads(handler.request.body)
    for institute_id in issue['facets']['institute']:
        authorize(user_id, institute_id)

    # Make available downstream.
    handler.user_id = user_id
    handler.issue = issue
