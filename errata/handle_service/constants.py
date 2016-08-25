# -*- coding: utf-8 -*-
"""
.. module:: handle_service.constants.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Handle service wrapper constants.

.. moduleauthor:: Atef Bennasser <abennasser@ipsl.jussieu.fr>


"""
# Misc
USERNAME = 'esgf-issue-manager'
REPO = 'ipsl'
BASE_API_URL = 'http://hdl.handle.net/api/handles/21.14100'
PORT = '21.14100'
HS_ADMIN = 'HS_ADMIN'
TYPE = 'type'
DATA = 'data'
VALUE = 'value'
VALUES = 'values'
HDL_PREFIX = 'hdl:'

# Aggregation levels:
AGGREGATION_LEVEL = 'AGGREGATION_LEVEL'
FILE_NAME = 'FILE_NAME'
FILE = 'FILE'
FILE_VERSION = 'FILE_VERSION'
DATASET = 'DATASET'
PARENTS = 'IS_PART_OF'
CHILDREN = 'HAS_PARTS'
DRS = 'DRS_ID'
VERSION = 'VERSION_NUMBER'

# Handle tree
PREDECESSOR = 'REPLACES'
SUCCESSOR = 'REPLACED_BY'

# Handle attributes
CHECKSUM = 'CHECKSUM'
ERRATA_IDS = 'ERRATA_IDS'
URL = 'URL'
