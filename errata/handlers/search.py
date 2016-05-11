# -*- coding: utf-8 -*-

"""
.. module:: handlers.search.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - search issues endpoint.

.. moduleauthor:: Atef Benasser <abenasser@ipsl.jussieu.fr>


"""
from errata import db
from errata.utils.http import HTTPRequestHandler
from errata.utils import logger


# Query parameter names.
_PARAM_STATE = 'state'
_PARAM_STATUS = 'status'
_PARAM_TIMESTAMP = 'timestamp'


def log_test(msg):
    """Logs a test message

    """
    # msg = "[{0}]: --> error --> {1} --> {2}"
    # msg = msg.format(id(self), self, error)
    logger.log_web(msg)


class SearchRequestHandler(HTTPRequestHandler):
    """Search issue request handler.

    """
    def __init__(self, application, request, **kwargs):
        """Instance constructor.

        """
        super(SearchRequestHandler, self).__init__(application, request, **kwargs)

        self.status = None
        self.timestamp = None
        self.issues = []
        self.total = 0


    def get(self):
        """HTTP GET handler.

        """
        def _decode_request():
            """Decodes request.

            """
            if self.get_argument(_PARAM_STATUS) != "*":
                logger.log_web("PARAM RECEIVED " + _PARAM_STATUS)
                self.status = self.get_argument(_PARAM_STATUS)

            if self.get_argument(_PARAM_TIMESTAMP) != "*":
                self.timestamp = self.get_argument(_PARAM_TIMESTAMP)


        def _set_data():
            """Pulls data from db.

            """
            with db.session.create():
                self.issues = db.dao.get_issues(status=self.status)
                self.total = db.utils.get_count(db.models.Issue)


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output_encoding = 'json'
            self.output = {
                'count': len(self.issues),
                'results': self.issues,
                'timestamp': self.timestamp,
                'total': self.total,
            }


        # Invoke tasks.
        # TODO input request validation.
        self.invoke([], [
            _decode_request,
            _set_data,
            _set_output
            ])
