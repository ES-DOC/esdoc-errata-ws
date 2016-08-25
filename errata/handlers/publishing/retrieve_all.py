# -*- coding: utf-8 -*-

"""
.. module:: handlers.retrieve.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - retrieve issue endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import tornado

from errata import db
from errata.utils import constants
from errata.utils import convertor
from errata.utils.http import process_request



class RetrieveAllIssuesRequestHandler(tornado.web.RequestHandler):
    """Retrieve issue request handler.

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
            self.issues = db.dao.get_all_issues()
            self.datasets = db.dao.get_issue_datasets()
            self.models = db.dao.get_issue_models()


        def _set_output():
            """Sets response to be returned to client.

            """
            def _encode(issue):
                """Encode issue as a simple dictionary.

                """
                obj = convertor.to_dict(issue)

                # Remove db injected fields.
                del obj['id']
                del obj['row_create_date']
                del obj['row_update_date']

                # Set array fields.
                obj['datasets'] = sorted([i[1] for i in self.datasets if i[0] == issue.uid])
                obj['materials'] = sorted(issue.materials.split(","))
                obj['models'] = sorted([i[1] for i in self.models if i[0] == issue.uid])

                return obj

            self.output = {
                'issues': [_encode(i) for i in self.issues]
            }


        # Process request.
        with db.session.create():
            process_request(self, [
                _set_data,
                _set_output
                ])
