import os

import tornado.web

from errata_ws import handlers
from errata_ws import schemas
from errata_ws.utils import config
from errata_ws.utils.logger import log_web as log



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
        (r'/', handlers.operations.FrontEndRequestHandler),
        (r'/status', handlers.operations.HeartbeatRequestHandler),
        (r'/oauth/authorize', handlers.operations.oauth.AuthorizeRequestHandler),
        (r'/oauth/callback', handlers.operations.oauth.CallbackRequestHandler),
        (r'/validate-dataset-id', handlers.operations.ValidateDatasetIdentifierRequestHandler),
        (r'/verify-authorization', handlers.operations.VerifyAuthorizationRequestHandler),

        # ... issue moderation
        (r'/2/issue/moderation/accept', handlers.moderation.AcceptIssueRequestHandler),
        (r'/2/issue/moderation/search', handlers.moderation.IssueSearchRequestHandler),
        (r'/2/issue/moderation/propose', handlers.moderation.ProposeIssueRequestHandler),
        (r'/2/issue/moderation/reject', handlers.moderation.RejectIssueRequestHandler),

        # ... issue publication
        (r'/2/issue/publication/close', handlers.publication.CloseIssueRequestHandler),
        (r'/2/issue/publication/create', handlers.publication.CreateIssueRequestHandler),
        (r'/2/issue/publication/retrieve', handlers.publication.RetrieveIssueRequestHandler),
        (r'/2/issue/publication/retrieve-all', handlers.publication.RetrieveAllIssuesRequestHandler),
        (r'/2/issue/publication/update', handlers.publication.UpdateIssueRequestHandler),

        # ... search
        (r'/2/issue/search', handlers.search.IssueSearchRequestHandler),
        (r'/2/issue/search-setup', handlers.search.IssueSearchSetupRequestHandler),

        # ... PID
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
