# -*- coding: utf-8 -*-

"""
.. module:: handlers.retrieve.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - retrieve issue endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import sys
sys.path.append('/home/abennasser/Bureau/esdoc-errata-updated-fe/esdoc-errata-master/ws')
from errata import db
from errata.utils.http import HTTPRequestHandler


# Query parameter names.
_PARAM_UID = 'uid'


class RetrieveRequestHandler(HTTPRequestHandler):
    """Retrieve issue request handler.

    """
    def __init__(self, application, request, **kwargs):
        """Instance constructor.

        """
        super(RetrieveRequestHandler, self).__init__(application, request, **kwargs)

        self.uid = None
        self.issue = None
        self.list_of_uids = None


    def get(self):
        """HTTP GET handler.

        """
        def _decode_request():
            """Decodes request.

            """
            self.uid = self.get_argument(_PARAM_UID)


        def _set_data():
            """Pulls data from db.

            """
            with db.session.create():
                # self.issues = db.dao.get_issues_by_uids(self.list_of_uids)
                self.issue = db.dao.get_issue(self.uid)

            print self.issue


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output_encoding = 'json'
            self.output = {
                'issue': self.issue
            }


        # Invoke tasks.
        # TODO input request validation.
        self.invoke([], [
            _decode_request,
            _set_data,
            _set_output
            ])


# list_of_uids = ["11221244-2194-4c1f-bdea-4887036a9e63", "11111111-1111-1111-1111-1111111111"]
# list = db.dao.get_issues_by_uids(list_of_uids)
# for item in list:
#     print item