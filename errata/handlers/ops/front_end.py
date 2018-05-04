# -*- coding: utf-8 -*-

"""
.. module:: handlers.heartbeat.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - heartbeat endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import datetime as dt

import tornado

import errata
from errata.utils.http import process_request



class FrontEndRequestHandler(tornado.web.RequestHandler):
    """Front end request handler.

    """
    def get(self):
        """HTTP GET handler.

        """
        # Calculate new url.
        url = '{}://{}/static/index.html'.format(
            self.request.protocol,
            self.request.host
            )

        # Redirect.
        self.redirect(url, permanent=False)
