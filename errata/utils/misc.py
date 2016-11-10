# -*- coding: utf-8 -*-
"""
.. module:: utils.misc.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Miscellaneous utility functions.

.. moduleauthor:: Guillaume Levavasseur <glipsl@ipsl.jussieu.fr>


"""
import base64
import requests
import json
from constants import ORGS_IDS


def traverse(target, tree_types=(list, tuple)):
    """Iterates through a list of lists and extracts items.

    :param object target: Target to be traversed.
    :param tuple tree_types: Iterable types

    :returns: An iterable list of extracted items.
    :rtype: generator

    """
    if isinstance(target, tree_types):
        for item in target:
            for child in traverse(item, tree_types):
                yield child
    else:
        yield target


def authenticate(requesthandler):
    """
    extracts auth header from request and queries github oauth api
    :param requesthandler: tornado request handler
    :return: nothing, unless it raises an exception
    """

    credentials = requesthandler.request.headers['Authorization']
    credentials = credentials.replace('Basic ', '')
    credentials = base64.b64decode(credentials).split(':')
    r = requests.get('https://api.github.com/user', auth=(credentials[0], credentials[1]))
    if r.status_code != 200:
        set_http_return(requesthandler, 401, 'Authentication failed, make sure your credentials are correct.')
    else:
        answer = json.loads(r.text.encode('ascii', 'ignore'))
        write_access = requests.get(answer["organizations_url"])
        orgs_dic = json.loads(write_access.text.encode('ascii', 'ignore'))
        has_priv = False
        for org in orgs_dic:
            if int(org['id']) in ORGS_IDS:
                has_priv = True
        if not has_priv:
            set_http_return(requesthandler, 403,  'User lacks required privilege, contact admins for further '
                                                  'information.')


def set_http_return(request_handler, http_code, msg):
    request_handler.clear()
    request_handler.set_status(http_code)
    request_handler.finish(msg)
