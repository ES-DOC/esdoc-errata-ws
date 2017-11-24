# -*- coding: utf-8 -*-
"""
.. module:: utils.misc.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Miscellaneous utility functions.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import pyesdoc

from errata.utils import config
from errata.utils import constants
from errata.utils import exceptions
from errata.utils import logger



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
    pyesdoc.authenticate_user(credentials)


def authorize(user_id, project_id, institute_id):
    """Authorizes user against GitHub team membership api.

    :param str user_id: GitHub username.
    :param str project_id: Project identifier, e.g. cmip6.
    :param str institute_id: Institute identifier, e.g. ipsl.

    """
    logger.log_web('Authorizing: {} --> {}'.format(user_id, _GH_TEAM))
    pyesdoc.authorize_user(_GH_TEAM, user_id)

    logger.log_web('Authorizing: {} --> {}-{}'.format(user_id, project_id, institute_id))
    pyesdoc.authorize_user('{}-{}'.format(project_id, institute_id), user_id)


def apply_policy(user_id, access_token, project_id, institute_id):
    """Applies security policy.

    :param str user_id: GitHub username.
    :param str access_token: GitHub access token.
    :param str institute_id: Institute identifier, e.g. ipsl.

    """
    authenticate((user_id, access_token))
    authorize(user_id, project_id, institute_id)


def secure_request(handler):
    """Enforces request level security policy (if necessary).

    :param utils.http.HTTPRequestHandler handler: An HTTP request handler.

    """
    # Escape if endpoint is whitelisted.
    if handler.request.path in _WHITELISTED_ENDPOINTS:
        return

    # Strip credentials.
    credentials = pyesdoc.strip_credentials(handler.request.headers['Authorization'])

    # Authenticate.
    if config.apply_security_policy:
        logger.log_web('Authenticating: {}'.format(credentials[0]))
        authenticate(credentials)

    # Make user-id available downstream.
    handler.user_id = credentials[0]
