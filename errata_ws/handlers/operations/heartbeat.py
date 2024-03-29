import datetime as dt

import tornado

import errata_ws
from errata_ws.utils.http import process_request



class HeartbeatRequestHandler(tornado.web.RequestHandler):
    """Operations heartbeat request handler.

    """
    def get(self):
        """HTTP GET handler.

        """
        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                "message": "ES-DOC ERRATA web service is operational @ {}".format(dt.datetime.utcnow()),
                "version": errata_ws.__version__
            }

        # Process request.
        process_request(self, _set_output)
