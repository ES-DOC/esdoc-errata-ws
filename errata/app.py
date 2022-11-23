# -*- coding: utf-8 -*-
"""

.. module:: app.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - web-service entry point.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import os

import tornado.web

from errata import handlers
from errata import schemas
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
    return {
        (r'/', handlers.ops.FrontEndRequestHandler),
        (r'/status', handlers.ops.HeartbeatRequestHandler),
        (r'/oauth/authorize', handlers.ops.oauth.AuthorizeRequestHandler),
        (r'/oauth/callback', handlers.ops.oauth.CallbackRequestHandler),
        (r'/validate-dataset-id', handlers.ops.ValidateDatasetIdentifierRequestHandler),
        (r'/verify-authorization', handlers.ops.VerifyAuthorizationRequestHandler),
        (r'/1/issue/accept', handlers.moderation.AcceptIssueRequestHandler),
        (r'/1/issue/close', handlers.publishing.CloseIssueRequestHandler),
        (r'/1/issue/create', handlers.publishing.CreateIssueRequestHandler),
        (r'/1/issue/extend', handlers.moderation.ExtendIssueRequestHandler),
        (r'/1/issue/update', handlers.publishing.UpdateIssueRequestHandler),
        (r'/1/issue/reject', handlers.moderation.RejectIssueRequestHandler),
        (r'/1/issue/retrieve', handlers.publishing.RetrieveIssueRequestHandler),
        (r'/1/issue/retrieve-all', handlers.publishing.RetrieveAllIssuesRequestHandler),
        (r'/1/issue/search', handlers.search.IssueSearchRequestHandler),
        (r'/1/issue/search-setup', handlers.search.IssueSearchSetupRequestHandler),
        (r'/1/pid-queue/search', handlers.search.PIDQueueSearchRequestHandler),
        (r'/1/pid-queue/search-setup', handlers.search.PIDQueueSearchSetupRequestHandler),
        (r'/1/resolve/pid', handlers.resolve.ResolvePIDRequestHandler),
        (r'/1/resolve/simple-pid', handlers.resolve.ResolveSimplePIDRequestHandler)
    }


def _get_app_settings():
    """Returns app settings.

    """
    return {
        "cookie_secret": config.cookie_secret,
        # "cookie_secret": os.urandom(24),
        "compress_response": True,
        "static_path": config.staticFilePath,
        "xsrf_cookies": True
    }


def _get_app():
    """Returns application instance.

    """
    endpoints = _get_app_endpoints()
    log("Endpoint to handler mappings:")
    for ep, handler in sorted(endpoints, key=lambda i: i[0]):
        log("{0} ---> {1}".format(ep, str(handler).split(".")[-1][0:-2]))


    schemas.init([i[0] for i in endpoints])
    return tornado.web.Application(endpoints,
                                   debug=True,
                                   **_get_app_settings())


def run():
    """Runs web service.

    """
    # Initialize application.
    log("Initializing")
    app = _get_app()

    # Open port.
    app.listen(config.port)
    log("Running @ port {}".format(config.port))

    # Start processing requests.
    tornado.ioloop.IOLoop.instance().start()


def stop():
    """Stops web service.

    """
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_callback(lambda x: x.stop(), ioloop)
