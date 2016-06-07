# -*- coding: utf-8 -*-

"""
.. module:: handlers.hs_handler.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - handle service search endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


WS return is a dictionary of dictionaries.

Structure of self.issues = {Queried_handle_1 : {Queried/Predecessors/Successors_handles : Issue ...}
                            , Queried_handle_2 : {Queried/Predecessors/Successors_handles : Issue ...}

"""
from errata import db
from errata.handle_service.harvest import harvest_errata_information
from errata.utils.http import HTTPRequestHandler
from errata.utils.http import HTTP_HEADER_Access_Control_Allow_Origin
import logging
import json

# Query parameter names.
_PARAM_HANDLES = 'handles'
_PARAM_TIMESTAMP = 'timestamp'

# Query parameter validation schema.
_REQUEST_VALIDATION_SCHEMA = {
    _PARAM_HANDLES: {
        'required': True,
        'type': 'list', 'schema': {'type': 'string'}
    },
    _PARAM_TIMESTAMP: {
        'required': True,
        'type': 'list', 'items': [{'type': 'string'}]
    }
}


class HandleServiceRequestHandler(HTTPRequestHandler):
    """Retrieve issue request handler.

    """
    def __init__(self, application, request, **kwargs):
        """Instance constructor.

        """
        super(HandleServiceRequestHandler, self).__init__(application, request, **kwargs)

        self.handles = []
        self.uid_list = dict()
        self.issues = None
        self.timestamp = None


    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(HTTP_HEADER_Access_Control_Allow_Origin, "*")


    def get(self):
        """HTTP GET handler.

        """
        def _decode_request():
            """Decodes request.

            """
            self.timestamp = self.get_argument(_PARAM_TIMESTAMP)
            self.handles = self.get_argument(_PARAM_HANDLES).split(",")


        def _invoke_pid_handle_service():
            """Invoke remote PID handle service.

            """
            for handle in self.handles:
                retrieved_tuple = harvest_errata_information(handle)
                self.uid_list[retrieved_tuple[1]] = retrieved_tuple[0]

        def _set_data():
            """Pulls data from db.

            """
            print "_set_data"
            with db.session.create():
                self.issues = dict()
                issue_dic = dict()
                for handle, uid_dic in self.uid_list.iteritems():
                    for dset_or_file_id, uid in uid_dic.iteritems():
                        # print uid
                        if uid[0] != '':
                            issue_dic[dset_or_file_id] = [uid[0], uid[1]]
                        else:
                            issue_dic[dset_or_file_id] = [uid[0], uid[1]]

                    self.issues[handle] = issue_dic
            logging.info('The json response is...')
            print json.dumps(self.issues)
            logging.info(json.dumps(self.issues))

        def _set_output():
            """Sets response to be returned to client.

            """
            self.output_encoding = 'json'
            self.output = {
                'issues': self.issues,
                'timestamp': self.timestamp
            }


        # Invoke tasks.
        self.invoke(_REQUEST_VALIDATION_SCHEMA, [
            _decode_request,
            _invoke_pid_handle_service,
            _set_data,
            _set_output
            ])
