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
from errata.utils.constants_json import FACET_TYPE_JSON_FIELD
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
        def _set_data():
            """Pulls data from db.

            """
            self.issue = db.dao.get_issue(self.get_argument(_PARAM_UID))
            self.facets = db.dao.get_issue_facets(self.get_argument(_PARAM_UID))


        def _set_output():
            """Sets response to be returned to client.

            """
            obj = convertor.to_dict(self.issue)
            obj['materials'] = sorted(self.issue.materials.split(","))
            for ft, jf in [(i, FACET_TYPE_JSON_FIELD[i]) for i in constants.FACET_TYPE]:
                if jf not in obj:
                    fv_list = [i[0] for i in self.facets if i[1] == ft]
                    obj[jf] = sorted(set(fv_list))

            self.output = {
                'issue': obj
            }


        # Process request.
        with db.session.create():
            process_request(self, [
                _set_data,
                _set_output
                ])
