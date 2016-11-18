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
    '/1/issue/search',
}

# Set of recognized organization identifiers.
# TODO: push to config
_ORGS_IDS = [23123271]


def _authenticate(handler):
    """Authenticate request against github oauth api.

    """
    # Set credentials to be passed to GitHub OAuth application.
    # TODO validate 'Authorization' header exists
    credentials = handler.request.headers['Authorization']
    credentials = credentials.replace('Basic ', '')
    credentials = base64.b64decode(credentials).split(':')

    # 401 if credentials unrecognized.
    r = requests.get('https://api.github.com/user', auth=(credentials[0], credentials[1]))
    if r.status_code != 200:
        set_http_return(handler, 401, "Credentials unrecognized.")
        raise exceptions.SecurityError("Credentials unrecognized.")

    return json.loads(r.text.encode('ascii', 'ignore'))


def _authorize(handler, user):
    """Authorize request against set of recognized organizations.

    """
    # Load set of organizations that user is a member of.
    write_access = requests.get(user["organizations_url"])
    orgs_dic = json.loads(write_access.text.encode('ascii', 'ignore'))

    # 403 if not a member of a recognized organization.
    is_authorized = bool([i for i in orgs_dic if i in _ORGS_IDS])
    if not is_authorized:
        set_http_return(handler, 403, "Insufficient privileges.")
        raise exceptions.SecurityError("Insufficient privileges.")


def set_http_return(request_handler, http_code, msg):
    request_handler.clear()
    request_handler.set_status(http_code)
    request_handler.finish(msg)


def secure_request(handler):
    """Enforces request level security policy (if necesaary).

    :param utils.http.HTTPRequestHandler handler: An HTTP request handler.

    :raises: exceptions.SecurityError

    """
    # Escape if not required.
    if not handler.request.path in _SECURED_ENDPOINTS:
        return

    return

    _authorize(handler, _authenticate(handler))
