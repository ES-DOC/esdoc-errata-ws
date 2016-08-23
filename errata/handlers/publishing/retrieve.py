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



# Query parameter names.
_PARAM_UID = 'uid'



class RetrieveIssueRequestHandler(tornado.web.RequestHandler):
    """Retrieve issue request handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(constants.HTTP_HEADER_Access_Control_Allow_Origin, "*")


    def get(self):
        """HTTP GET handler.

        """
        def _decode_request():
            """Decodes request.

            """
            global uid

            uid = self.get_argument(_PARAM_UID)


        def _set_data():
            """Pulls data from db.

            """
            global issue, uid, datasets, models

            with db.session.create():
                issue = db.dao.get_issue(uid)
                datasets = db.dao.get_issue_datasets(issue.uid)
                models = db.dao.get_issue_models(issue.uid)


        def _set_output():
            """Sets response to be returned to client.

            """
            global issue, datasets, models

            # Encode issue as a simple dictionary.
            obj = convertor.to_dict(issue)

            # Remove db injected fields.
            del obj['id']
            del obj['row_create_date']
            del obj['row_update_date']

            # Set array fields.
            obj['datasets'] = datasets
            obj['materials'] = sorted(issue.materials.split(","))
            obj['models'] = models

            self.output = {
                'issue': obj
            }


        # Initialize shared processing variables.
        datasets = issue = models = uid = None

        # Process request.
        process_request(self, [
            _decode_request,
            _set_data,
            _set_output
            ])
