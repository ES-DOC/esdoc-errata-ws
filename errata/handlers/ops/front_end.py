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


# Query parameter names.
_PARAM_PROJECT = 'project'
_PARAM_INSTITUTE = 'institute'
_PARAM_EXPERIMENT = 'experiment'
_PARAM_MODEL = 'model'
_PARAM_SOURCE = 'source'
_PARAM_VARIABLE = 'variable'

# Query parameters.
_PARAMS = {
    'project',
    'institute',
    'experiment',
    'model',
    'source',
    'variable'
}


class FrontEndRequestHandler(tornado.web.RequestHandler):
    """Front end request handler.

    """
    def get(self):
        """HTTP GET handler.

        """
        # Set url.
        url = '{}://{}/static/index.html'.format(
            self.request.protocol,
            self.request.host
            )

        # Set url params.
        params = (i for i in _PARAMS if self.get_argument(i, None))
        for idx, param in enumerate(sorted(params)):
            seperator = '?' if idx == 0 else '&'
            url = '{}{}{}={}'.format(url, seperator, param, self.get_argument(param))

        # Redirect.
        self.redirect(url, permanent=False)
