    # -*- coding: utf-8 -*-

"""
.. module:: handlers.search_setup.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - search setup endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import collections
import operator

import tornado

import pyessv

from errata import db
from errata.utils import constants
from errata.utils.http import process_request



class IssueSearchSetupRequestHandler(tornado.web.RequestHandler):
    """Search issue request handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        self.set_header(constants.HTTP_HEADER_Access_Control_Allow_Origin, "*")


    def get(self):
        """HTTP GET handler.

        """
        def _get_facet_data(facet_types):
            result = []
            facets = db.dao.get_project_facets()
            for facet_type in facet_types:
                result.append({
                    'key': facet_type.namespace,
                    'label': facet_type.label,
                    'values': [i[2] for i in facets if i[1] == facet_type.namespace]
                    })

            return result



        def _set_output():
            """Sets response to be returned to client.

            """
            # Set facet types.
            facet_types = {
                'esdoc:errata:project',
                'esdoc:errata:severity',
                'esdoc:errata:status',
            }
            for project in pyessv.load('esdoc:errata:project'):
                for facet_type in project.data['facets']:
                    facet_types.add(facet_type)

            # Get facet values.
            with db.session.create():
                facet_values = set(db.dao.get_project_facets())

            # Set output.
            self.output = {
                'vocabs': [_map_collection(i) for i in sorted(facet_types)],
                'values': facet_values
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
        'key': term.namespace,
        'canonicalName': term.canonical_name,
        # 'key': term.canonical_name,
        'namespace': term.namespace,
        'label': term.label,
    }
    result.update(term.data)

    return result
