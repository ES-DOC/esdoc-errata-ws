import tornado

import pyessv

from errata import db
from errata.utils import constants
from errata.utils.http import process_request



class PIDQueueSearchSetupRequestHandler(tornado.web.RequestHandler):
    """Search PID queue request handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(constants.HTTP_HEADER_Access_Control_Allow_Origin, "*")


    def get(self):
        """HTTP GET handler.

        """
        def _set_output():
            """Sets response to be returned to client.

            """
            # Set vocabs to be loaded.
            vocabs = [
                'esdoc:errata:project',
                'esdoc:errata:pid-task-action',
                'esdoc:errata:pid-task-status'
            ]

            # Set output.
            self.output = {
                'vocabs': [_map_collection(i) for i in vocabs],
            }


        # Process request.
        process_request(self, _set_output)


def _map_collection(identifier):
    """Converts a pyessv collection to a dictionary.

    """
    collection = pyessv.load(identifier)

    result = {
        'key': collection.namespace,
        'label': collection.label,
        'terms': [_map_term(i) for i in collection]
    }
    if collection.data is not None:
        result.update(collection.data)

    return result


def _map_term(term):
    """Converts a pyessv term to a dictionary.

    """
    result = {
        'canonical_name': term.canonical_name,
        'key': term.namespace,
        'namespace': term.namespace,
        'label': term.label,
    }
    result.update(term.data)

    return result