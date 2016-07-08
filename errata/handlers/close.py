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


# Query parameter names.
_PARAM_UID = 'uid'

# Query parameter validation schema.
_REQUEST_VALIDATION_SCHEMA = {
    _PARAM_UID: {
        'required': True,
        'type': 'list', 'items': [{'type': 'uuid'}]
    }
}


def _validate_json(request):
    """
    This will be the validation process of the incoming json request.
    Any creation or update request needs to be conform with a set of rules.
    :param request: json request
    :return: valid or not
    """
    pass


class CloseRequestHandler(HTTPRequestHandler):
    """issue handler.

    """
    def __init__(self, application, request, **kwargs):
        """Instance constructor.

        """
        super(CloseRequestHandler, self).__init__(application, request, **kwargs)

    def put(self):
        """
        HTTP PUT HANDLER
        """
        def _decode_request():
            self.uid = self.get_argument(_PARAM_UID)

        def _invoke_issue_handler():
            close(self.uid)

        def _set_output():
            self.output = {
                "status": 0
            }

        self.invoke(None, [_decode_request, _invoke_issue_handler, _set_output])

