# -*- coding: utf-8 -*-
"""
.. module:: utils.http_invoker.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: HTTP request handler task invoker.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from errata.utils import logger



def log(handler, msg, is_error=False):
    """Logs an error response.

    """
    print msg
    msg = "[{}]: --> {}".format(id(handler), msg)
    print msg
    if is_error:
        logger.log_web_error(msg)
    logger.log_web(msg)


def log_error(handler, error):
    """Logs an error response.

    """
    log(handler, "error --> {} --> {}".format(handler, error), True)


def log_success(handler):
    """Logs a successful response.

    """
    log(handler, "success --> {}".format(handler))

