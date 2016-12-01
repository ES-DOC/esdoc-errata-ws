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



# Set of secured endpoints.
_SECURED_ENDPOINTS = {
    '/1/issue/close',
    '/1/issue/create',
    '/1/issue/update',
}

# GitHub API - user details.
_GH_API_USER = 'https://api.github.com/user'

# ESDOC GitHub organization identifier.
_ESDOC_GH_ORG_ID = 1415530

# ESDOC GitHub team: errata-publication
_ESDOC_GH_TEAM_ERRATA_PUBLICATION = 'errata-publication'

# Whitelist of trusted organizations.
_GH_ORGS_WHITELIST = set([
    _ESDOC_GH_ORG_ID
    ])


def _authenticate(handler):
    """Authenticate request against github oauth api.

    """
    # Extract credentials from request header.
    credentials = handler.request.headers['Authorization']
    credentials = credentials.replace('Basic ', '')
    credentials = tuple(base64.b64decode(credentials).split(':'))

    # Authenticate against GitHub API.
    r = requests.get(_GH_API_USER, auth=credentials)

    # Fail: throw exception.
    if r.status_code != 200:
        raise exceptions.RequestAuthenticationError()

    # Success: therefore return GH user information.
    return json.loads(r.text)


def _authorize(handler, user):
    """Authorize request against set of recognized organizations.

    """
    # TODO apply scope check: read:org


    # Load user GitHub organization membership.
    r = requests.get(user["organizations_url"])
    membership = set(i['id'] for i in json.loads(r.text))

    # Authorization failure if user is not a member of any recognized organization.
    if not bool(_GH_ORGS_WHITELIST.intersection(membership)):
        raise exceptions.RequestAuthorizationError()


def secure_request(handler):
    """Enforces request level security policy (if necesaary).

    Policy is as follows:
    1.  Authenticate via GitHub user API.
    2.  Authorize by confirming user is public member of GitHub oranization whitelist.

    Alternative policy is to authenticate as now then
    check if user is public member of ES-DOC GH org &
    then if member of ES-DOC GH errata-publishers team

    :param utils.http.HTTPRequestHandler handler: An HTTP request handler.

    :raises: exceptions.SecurityError

    """
    return

    # Escape if not required.
    if not handler.request.path.split("?")[0] in _SECURED_ENDPOINTS:
        return

    # Authenticates then authorizes.
    _authorize(handler, _authenticate(handler))
