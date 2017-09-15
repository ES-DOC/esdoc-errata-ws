# -*- coding: utf-8 -*-
"""
.. module:: utils.config.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Configuration utility functions.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import os
import logger
import requests
import json

from ConfigParser import ConfigParser
from errata.utils.convertor import json_file_to_namedtuple
from time import time
from StringIO import StringIO

# Default configuration file path.
_CONFIG_FPATH = "ws.conf"

# Configuration data.
data = None
facet_cf = None
GH_FILE_API = 'https://api.github.com/repos/ESGF/config/contents/publisher-configs/ini/esg.{}.ini?ref=devel'
FILE_EXPIRATION_TIME = 15
DOWNLOAD_URL = 'download_url'


def _get_config_fpath(config_path):
    """Returns configuration file path.

    """
    dpath = os.path.dirname(os.path.abspath(__file__))
    while dpath != '/':
        fpath = os.path.join(dpath, "ops/config")
        fpath = os.path.join(fpath, config_path)
        if os.path.exists(fpath):
            return fpath
        dpath = os.path.dirname(dpath)

    err = "ESDOC-ERRATA configuration file ({0}) could not be found".format(config_path)
    raise RuntimeError(err)


def _get_remote_config(project):
    """
    Using github api, this returns config file contents.
    :param project: str
    :return: ConfigParser instance with proper configuration
    """
    project_ini_file = 'esg.{}.ini'.format(project)
    config = ConfigParser()
    if os.environ.get('ERRATA_WS_HOME'):
        project_ini_file = os.path.join(os.environ.get('ERRATA_WS_HOME'), 'ops/config/'+project_ini_file)
    else:
        project_ini_file = '.'+project_ini_file
    if os.path.isfile(project_ini_file) and (time()-os.path.getmtime(project_ini_file))/60 < FILE_EXPIRATION_TIME:
        # Reading local file.
        logger.log_web('RECENT PROJECT CONFIGURATION FILE FOUND LOCALLY. READING...')
        return
    else:
        r = requests.get(GH_FILE_API.format(project))
        if r.status_code == 200:
            logger.log_web('NO LOCAL PROJECT CONFIG FILE FOUND OR DEPRECATED FILE FOUND, RETRIEVING FROM REPO...')
            # Retrieving distant configuration file
            raw_file = requests.get(r.json()[DOWNLOAD_URL])
            config.readfp(StringIO(raw_file.text))
            logger.log_web('FILE RETRIEVED, PERSISTING LOCALLY...')
            # Keeping local copy
            with open(project_ini_file, 'w') as project_file:
                config.write(project_file)
            logger.log_web('FILE PERSISTED.')
            return
        else:
            raise Exception('CONFIG FILE NOT FOUND {}.'.format(r.status_code))


def _get_facet_config(project):
    """
    reads and digests facets dictionary
    :return:
    """
    with open(os.path.join(os.environ.get('ERRATA_WS_HOME'), 'resources/facets.json')) as facets_json_file:
        facets_dict = json.load(facets_json_file)
    return facets_dict[project]


def _init():
    """Initializes configuration.

    """
    global data
    # global facet_cf

    # Get configuration file path (falling back to template if necessary).
    fpath = _get_config_fpath('ws.conf')
    # Getting facets dictionary
    # facet_cf = json_file_to_namedtuple(os.path.join(os.environ.get('ERRATA_WS_HOME'), 'resources/facets.json'))
    # Convert config file to a named tuple.
    data = json_file_to_namedtuple(fpath)

    logger.log_web("Configuration file loaded @ {}".format(fpath))


# Auto-initialize.
_init()

