# -*- coding: utf-8 -*-
"""
.. module:: utils.errata.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - logging utility functions.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import os

from errata.utils.convert import json_file_to_namedtuple

# Default configuration file path.
_CONFIG_FPATH = "template-errata-ws.conf"

# Configuration data.
data = None


def _init():
    """Initializes configuration."""
    global data
    # Search up file system hierarchy.
    dpath = os.path.dirname(os.path.abspath(__file__))
    while dpath != '/':
        fpath = os.path.join(dpath, _CONFIG_FPATH)
        if os.path.exists(fpath):
            break
        dpath = os.path.dirname(dpath)
    # If still not found then exception.
    if not os.path.exists(fpath):
        msg = "ESDOC-ERRATA configuration file ({0}) could not be found".format(_CONFIG_FPATH)
        raise RuntimeError(msg)
    # Config data wrapper.
    data = json_file_to_namedtuple(fpath)


# Auto-initialize.
_init()
