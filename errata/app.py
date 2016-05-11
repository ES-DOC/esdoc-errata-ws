# -*- coding: utf-8 -*-
"""

.. module:: app.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - web-service entry point.

.. moduleauthor:: Atef Benasser <abenasser@ipsl.jussieu.fr>


"""
import os

import tornado.web

from errata import handlers
from errata.utils import config
from errata.utils.logger import log_web as log



def _get_path_to_front_end():
    """Return path to the front end javascript application.

    """
    dpath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'fe')
    log("Front-end static files @ {0}".format(dpath))

    return dpath


def _get_app_endpoints():
    """Returns map of application endpoints to handlers.

    """
    endpoints = {
        (r'/', handlers.HeartbeatRequestHandler),
        (r'/1/issue/retrieve', handlers.RetrieveRequestHandler),
        (r'/1/issue/search', handlers.SearchRequestHandler),
        (r'/1/issue/search/setup', handlers.SearchSetupRequestHandler),
        (r'/1/issue/handler', handlers.HandleServiceRequestHandler),

    }

    log("Endpoint to handler mappings:")
    for url, handler in sorted(endpoints, key=lambda ep: ep[0]):
        log("{0} ---> {1}".format(url, handler))

    return endpoints


def _get_app_settings():
    """Returns app settings.

    """
    return {
        "cookie_secret": config.cookie_secret,
        "compress_response": True,
        "static_path": _get_path_to_front_end()
    }


def _get_app():
    """Returns application instance.

    """
    return tornado.web.Application(_get_app_endpoints(),
                                   debug=True,
                                   **_get_app_settings())


def run():
    """Runs web service.

    """
    log("Initializing")

    # Run web-service.
    app = _get_app()
    app.listen(config.port)
    log("Ready")

    tornado.ioloop.IOLoop.instance().start()


def stop():
    """Stops web service.

    """
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_callback(lambda x: x.stop(), ioloop)


# print _get_app_endpoints()