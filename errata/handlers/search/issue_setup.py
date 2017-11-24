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


        # def _get_project_data(facet_types):
        #     """Returns project setup data.

        #     """
        #     def _map_facet(key, values):
        #         return {
        #             'key': key,
        #             'label': '{}{}'.format(key[0].upper(), key[1:]),
        #             'values': values
        #         }

        #     def _map_project(key, facets):
        #         return {
        #             'key': key,
        #             'label': key.upper(),
        #             'facets': [_map_facet(k, v) for k, v in facets.items()]
        #         }

        #     def _get_data():
        #         result = collections.defaultdict(lambda : collections.defaultdict(list))
        #         facets = db.dao.get_project_facets(facet_types)
        #         for project, facet_type, facet_value in facets:
        #             result[project][facet_type].append(facet_value)

        #         return result.items()

        #     return [_map_project(k, v) for k, v in _get_data()]


        def _set_output():
            """Sets response to be returned to client.

            """
            facet_types = reduce(operator.add, [i.data['facets'] for i in pyessv.load('esdoc:errata:project')], [])
            with db.session.create():
                for i in db.dao.get_project_facets():
                    print i

            # print facet_types


            # with db.session.create():
            #     projects = [_map_term(i) for i in pyessv.load('esdoc:errata:project')]
            #     facets = []
            #     for project in projects:
            #         facets += [pyessv.load(i) for i in project['facets']]


            self.output = {
                'data': [_map_collection(i) for i in {
                    'esdoc:errata:project',
                    'esdoc:errata:severity',
                    'esdoc:errata:status',
                }],
                'facets': []
            }

        # Process request.
        process_request(self, _set_output)


def _map_collection(identifier):
    """Converts a pyessv collection to a dictionary.

    """
    collection = pyessv.load(identifier)

    return {
        'key': collection.namespace,
        'label': collection.label,
        'values': [_map_term(i) for i in collection]
    }


def _map_term(term):
    """Converts a pyessv term to a dictionary.

    """
    result = {
        'key': term.canonical_name,
        'namespace': term.namespace,
        'label': term.label,
    }
    result.update(term.data)

    return result
