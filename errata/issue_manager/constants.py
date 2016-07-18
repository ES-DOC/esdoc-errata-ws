# -*- coding: utf-8 -*-

"""
.. module:: errata.issue_manager.constants.py
   :platform: Unix
   :synopsis: Constants used in this module for better readability of code.

.. moduleauthor:: Guillaume Levavasseur <glipsl@ipsl.jussieu.fr>


"""

import os

# Rabbit MQ unsent messages directory
__UNSENT_MESSAGES_DIR__ = "{0}/unsent_rabbit_messages".format(os.path.dirname(os.path.abspath(__file__)))

# JSON issue schemas full path
__JSON_SCHEMA_PATHS__ = {'create': '{0}/schemas/create.json'.format(os.path.dirname(os.path.abspath(__file__))),
                         'update': '{0}/schemas/update.json'.format(os.path.dirname(os.path.abspath(__file__))),
                         'close': '{0}/schemas/update.json'.format(os.path.dirname(os.path.abspath(__file__))),
                         'retrieve': '{0}/schemas/retrieve.json'.format(os.path.dirname(os.path.abspath(__file__)))}
# List of keys that cannot be updated
NON_CHANGEABLE_KEYS = ['title', 'project', 'institute', 'date_created', 'date_updated']

# Ratio of similarity between descriptions of updated and database issue.
RATIO = 20

SUCCESS_MESSAGE = 'UPDATE SUCCEEDED.'
