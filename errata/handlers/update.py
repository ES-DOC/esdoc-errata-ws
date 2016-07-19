# -*- coding: utf-8 -*-

"""
.. module:: handlers.hs_handler.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - handle service search endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
from errata.issue_manager.manager import *
from errata.utils.http import HTTPRequestHandler
import json


def _validate_json(request):
    """
    This will be the validation process of the incoming json request.
    Any creation or update request needs to be conform with a set of rules.
    :param request: json request
    :return: valid or not
    """
    pass


class UpdateRequestHandler(HTTPRequestHandler):
    """issue handler.

    """
    def __init__(self, application, request, **kwargs):
        """Instance constructor.

        """
        super(UpdateRequestHandler, self).__init__(application, request, **kwargs)
        self.json_body = None

    def post(self):
        """
        HTTP POST HANDLER
        """
        def _decode_request():
            self.json_body = json.loads(self.request.body)

        def _invoke_issue_handler():
            issue = self.json_body
            self.message, self.status = update(issue)

        def _set_output():
            self.output = {
                'message': self.message,
                'status': self.status
            }

        self.invoke(None, [_decode_request, _invoke_issue_handler, _set_output])