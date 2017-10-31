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



def get_active_project(canonical_name):
    """Returns a project's configuration information.

    :str canonical_name: A project code.

    :returns: Project configuration.
    :rtype: dict

    """
    return _get_project(canonical_name, get_active_projects)


def get_active_projects():
    """Returns set of active projects.

    """
    return [i for i in get_projects() if i['is_active']]


def get_project(canonical_name):
    """Returns project specific configuration information.

    :str canonical_name: A project code.

    :returns: Project configuration.
    :rtype: dict

    """
    return _get_project(canonical_name, get_projects)


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


def validate(project, facets):
    """Validates a project and associated facets.

    :param str project: Project code.
    :param dict facets: Set of facets.

    """
    # Validate project is active.
    cfg = get_active_project(project)
    if cfg is None:
        raise exceptions.UnknownProjectError(project)

    # Validate facet types are valid.
    for facet_type in facets:
        if facet_type not in cfg['facets']:
            raise exceptions.UnknownFacetError(project, facet_type)

    # Validate facet values are valid.
    for facet_type, facet_values in facets.items():
        facet_conf = cfg['facets'][facet_type]
        collection_namespace = facet_conf['collection'].namespace
        for facet_value in facet_values:
            facet_namespace = '{}:{}'.format(collection_namespace, facet_value)
            if pyessv.parse_namespace(facet_namespace, strictness=3) is None:
                raise exceptions.InvalidFacetError(project, facet_type, facet_value)


def validate_facet_value(project, facet_type, facet_value):
    """Validates a project and associated facets.

    :param str project: Project code.
    :param dict facets: Set of facets.

    """
    # Validate project is active.
    cfg = get_active_project(project)
    if cfg is None:
        raise exceptions.UnknownProjectError(project)

    # Validate facet type is valid.
    facet_type = convertor.to_underscore_case(facet_type)
    if facet_type not in cfg['facets']:
        raise exceptions.UnknownFacetError(project, facet_type)

    # Validate facet value is valid.
    namespace = cfg['facets'][facet_type]['collection'].namespace
    namespace = '{}:{}'.format(namespace, facet_value)
    if pyessv.parse_namespace(namespace, strictness=3) is None:
        raise exceptions.InvalidFacetError(project, facet_type, facet_value)


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


def _get_project(canonical_name, collection):
    """Returns a project's configuration information.

    """
    for cfg in collection():
        if cfg['canonical_name'] == canonical_name:
            return cfg


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
