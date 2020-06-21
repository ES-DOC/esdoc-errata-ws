# -*- coding: utf-8 -*-
"""
.. module:: utils.http_security.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Miscellaneous utility functions.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from errata.utils import config
from errata.utils import logger
from errata.utils import security



# GitHub team name.
_GH_TEAM = 'errata-publication'

# Set of whitelisted endpoints.
_WHITELISTED_ENDPOINTS = {
    '/',
    '/status',
    '/validate-dataset-id',
    '/verify-authorization',
    '/1/issue/retrieve',
    '/1/issue/retrieve-all',
    '/1/issue/search',
    '/1/issue/search-setup',
    '/1/pid-queue/search',
    '/1/pid-queue/search-setup',
    '/1/resolve/issue',
    '/1/resolve/pid',
    '/1/resolve/simple-pid'
}


def apply_policy(user_id, access_token, project_id, institute_id):
    """Applies security policy.

    :param str user_id: GitHub username.
    :param str access_token: GitHub access token.
    :param str institute_id: Institute identifier, e.g. ipsl.

    """
    authenticate((user_id, access_token))
    authorize(user_id, project_id, institute_id)


def authenticate(credentials):
    """Authenticates user credentials request against GitHub user api.

    :param tuple credentials: 2 member tuple (GitHub username, GitHub access token)

    :returns: GitHub username
    :rtype: str

    """
    security.authenticate_user(credentials)


def authorize(user_id, project_id, institute_id):
    """Authorizes user against GitHub team membership api.

    :param str user_id: GitHub username.
    :param str project_id: Project identifier, e.g. cmip6.
    :param str institute_id: Institute identifier, e.g. ipsl.

    """
    # User must be a member of errata-publication team.
    logger.log_web('Authorizing: {} --> {}'.format(user_id, _GH_TEAM))
    security.authorize_user(_GH_TEAM, user_id)

    # User must be a member of {project}-{institute} specific team, e.g. cmip6-ipsl.
    logger.log_web('Authorizing: {} --> {}-{}'.format(user_id, project_id, institute_id))
    security.authorize_user('{}-{}'.format(project_id, institute_id), user_id)


def secure_request(handler):
    """Enforces request level security policy (if necessary).

    :param utils.http.HTTPRequestHandler handler: An HTTP request handler.

    """
    # Escape if endpoint is whitelisted.
    if handler.request.path in _WHITELISTED_ENDPOINTS:
        return

    # Set credentials - either from web-form or cli client.
    credentials = handler.get_secure_cookie('errata-oauth-credentials') or \
                  handler.request.headers['Authorization']

    # Strip credentials - i.e. destructure from b64 --> 2 member tuple.
    credentials = security.strip_credentials(credentials)

    # Authenticate.
    if config.apply_security_policy:
        logger.log_web('Authenticating: {}'.format(credentials[0]))
        authenticate(credentials)

    # Make user-id available downstream.
    handler.user_id = credentials[0]
