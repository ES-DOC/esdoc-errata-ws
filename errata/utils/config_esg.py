# -*- coding: utf-8 -*-
"""
.. module:: utils.config.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Configuration utility functions.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import os
import json

import pyessv

from errata.utils import exceptions
from errata.utils import convertor



# Projects configuration.
_PROJECTS = None



def get_project(canonical_name):
    """Returns project specific configuration information.

    :str canonical_name: A project code.

    :returns: Project configuration.
    :rtype: dict

    """
    for cfg in get_projects():
        if cfg['canonical_name'] == canonical_name:
            return cfg


def get_projects():
    """Returns a project's configuration information.

    :returns: Project configuration.
    :rtype: dict

    """
    global _PROJECTS

    if _PROJECTS is None:
        fpath = _get_projects_fpath()
        with open(fpath, 'r') as fstream:
            _PROJECTS = json.load(fstream)
        for key, value in _PROJECTS.items():
            _map_project(key, value)

    return _PROJECTS.values()


def _map_project(canonical_name, obj):
    """Transforms project configuration for ease of use downstream.

    """
    obj['canonical_name'] = canonical_name
    obj['facets'] = {k: {
        'name': k,
        'label': v,
        'collection': pyessv.load(v)
    } for k, v in obj.get('facets', dict()).items()}

    return obj


def _get_projects_fpath():
    """Returns path to projects configuration files.

    :returns: Path to projects configuration file.
    :rtype: str

    """
    fname = 'projects.json'
    fpath = os.getenv('ERRATA_WS_HOME')
    fpath = os.path.join(fpath, 'ops')
    fpath = os.path.join(fpath, 'config')
    fpath = os.path.join(fpath, fname)
    if not os.path.isfile(fpath):
        raise ValueError('ESG projects config file not found: {}'.format(fname))

    return fpath
