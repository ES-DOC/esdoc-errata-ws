import pyessv
import tornado

from errata import db
from errata.utils import http_security
from errata.utils.http import process_request



class IssueSearchSetupRequestHandler(tornado.web.RequestHandler):
    """Search issue request handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        http_security.set_headers(self)


    def get(self):
        """HTTP GET handler.

        """
        def _set_output():
            """Sets response to be returned to client.

            """
            # Set vocabs to be loaded.
            vocabs = {
                'esdoc:errata:project',
                'esdoc:errata:severity',
                'esdoc:errata:status',
            }
            for project in pyessv.load('esdoc:errata:project'):
                for vocab in project.data['facets']:
                    vocabs.add(vocab)

            # Get facet values.
            with db.session.create():
                facet_values = set(db.dao.get_project_facets())                

            # Set output.
            self.output = {
                'vocabs': [_map_collection(i) for i in sorted(vocabs)],
                'values': facet_values
            }

        # Process request.
        process_request(self, _set_output)


def _map_collection(identifier):
    """Converts a pyessv collection to a dictionary.

    """
    collection = pyessv.load(identifier)

    result = {
        'canonical_name': collection.canonical_name,
        'key': collection.namespace,
        'label': collection.label,
        'namespace': collection.namespace,
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
        'label': term.label,
        'namespace': term.namespace
    }
    result.update(term.data)

    return result
