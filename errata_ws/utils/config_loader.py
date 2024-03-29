import os
import logger
import json

from errata_ws.utils.convertor import json_file_to_namedtuple



# Default configuration file path.
_CONFIG_FPATH = "ws.conf"

# Configuration data.
data = None


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


def _init():
    """Initializes configuration.

    """
    global data

    # Get configuration file path (falling back to template if necessary).
    fpath = _get_config_fpath('ws.conf')

    # Convert config file to a named tuple.
    data = json_file_to_namedtuple(fpath)

    logger.log_web("Configuration file loaded @ {}".format(fpath))


# Auto-initialize.
_init()
