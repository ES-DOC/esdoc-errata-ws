# -*- coding: utf-8 -*-

"""
.. module:: handlers.search.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - search issues endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import tornado

from errata import db
from errata.utils import constants
from errata.utils.http import process_request



class PIDQueueSearchRequestHandler(tornado.web.RequestHandler):
    """Search PID queue request handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(constants.HTTP_HEADER_Access_Control_Allow_Origin, "*")


    def get(self):
        """HTTP GET handler.

        """
        def _set_data():
            """Pulls data from db.

            """
            with db.session.create():
                self.tasks = db.dao.get_pid_service_tasks()


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                'count': len(self.tasks),
                'results': self.tasks
            }


        # Process request.
        process_request(self, [
            _set_data,
            _set_output
            ])
