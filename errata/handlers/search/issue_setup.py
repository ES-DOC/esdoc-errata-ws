# -*- coding: utf-8 -*-

"""
.. module:: handlers.search_setup.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - search setup endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import collections

import tornado

from errata import db
from errata.utils import config_esg
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
        def _get_project_data():
            """Returns project setup data.

            """
            def _map_facet(key, values):
                return {
                    'key': key,
                    'label': '{}{}'.format(key[0].upper(), key[1:]),
                    'values': values
                }

            def _map_project(key, facets):
                return {
                    'key': key,
                    'label': key.upper(),
                    'facets': [_map_facet(k, v) for k, v in facets.items()]
                }

            def _get_data():
                result = collections.defaultdict(lambda : collections.defaultdict(list))
                facets = db.dao.retrieve_facets(excluded=['dataset', 'project', 'status', 'severity'])
                for project, facet_type, facet_value in facets:
                    result[project][facet_type].append(facet_value)

                return result.items()

            return [_map_project(k, v) for k, v in _get_data()]


        def _set_output():
            """Sets response to be returned to client.

            """
            with db.session.create():
                self.output = {
                    'project': _get_project_data(),
                    'severity': constants.SEVERITY,
                    'status': constants.STATUS
                }


        # Process request.
        process_request(self, _set_output)
