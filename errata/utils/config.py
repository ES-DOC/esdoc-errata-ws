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

from errata.utils.convertor import json_file_to_namedtuple



# Default configuration file path.
_CONFIG_FPATH = "errata-ws.conf"

# Configuration data.
data = None


def _get_config_fpath(prefix=""):
    cfg_fpath = "{}{}".format(prefix, _CONFIG_FPATH)
    dpath = os.path.dirname(os.path.abspath(__file__))
    while dpath != '/':
        fpath = os.path.join(dpath, cfg_fpath)
        if os.path.exists(fpath):
            return fpath
        dpath = os.path.dirname(dpath)

    err = "ESDOC-ERRATA configuration file ({0}) could not be found".format(_CONFIG_FPATH)
    raise RuntimeError(err)


def _init():
    """Initializes configuration.

    """
    global data

    # Get configuration file path (falling back to template if necessary).
    try:
        fpath = _get_config_fpath()
    except RuntimeError:
        fpath = _get_config_fpath("template-")

    # Convert config file to a named tuple.
    data = json_file_to_namedtuple(fpath)

    logger.log_web("Configuration file loaded @ {}".format(fpath))


# Auto-initialize.
_init()

