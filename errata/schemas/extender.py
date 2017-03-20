# -*- coding: utf-8 -*-
"""

.. module:: schemas.extender.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - endpoint validation schema cache extender.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import collections

from errata.utils import constants


# Schema extender functions mapped by schema type and endpoint.
_EXTENDERS = collections.defaultdict(dict)


def extend(schema, typeof, endpoint):
	"""Extends a JSON schema with data pulled from controlled vocabularies.

	:param dict schema: A JSON schema being extended.
	:param str typeof: Type of JSON schema to be extended.
	:param str endpoint: Endpoint being mapped to a JSON schema.

	"""
	try:
		extender = _EXTENDERS[endpoint][typeof]
	except KeyError:
		pass
	else:
		extender(schema)


def _1_issue_search_params(schema):
	"""Extends a JSON schema used to validate an HTTP operatino.

	"""
	schema['properties']['institute']['items']['enum'] += \
		[i['key'] for i in constants.INSTITUTE]
	schema['properties']['project']['items']['enum'] += \
		[i['key'] for i in constants.PROJECT]
	schema['properties']['severity']['items']['enum'] += \
		[i['key'] for i in constants.SEVERITY]
	schema['properties']['status']['items']['enum'] += \
		[i['key'] for i in constants.STATUS]


def _1_issue_close_params(schema):
	"""Extends a JSON schema used to validate an HTTP operation.

	"""
	schema['properties']['status']['items']['enum'] += \
		[i['key'] for i in constants.STATUS]


def _1_issue_create_body(schema):
	"""Extends a JSON schema used to validate an HTTP operation.

	"""
	schema['properties']['institution_id']['enum'] = \
		[i['key'] for i in constants.INSTITUTE]
	schema['properties']['mip_era']['enum'] = \
		[i['key'] for i in constants.PROJECT]
	schema['properties']['severity']['enum'] = \
		[i['key'] for i in constants.SEVERITY]
	schema['properties']['status']['enum'] = \
		[i['key'] for i in constants.STATUS]


def _1_issue_update_body(schema):
	"""Extends a JSON schema used to validate an HTTP operation.

	"""
	schema['properties']['institution_id']['enum'] = \
		[i['key'] for i in constants.INSTITUTE]
	schema['properties']['mip_era']['enum'] = \
		[i['key'] for i in constants.PROJECT]
	schema['properties']['severity']['enum'] = \
		[i['key'] for i in constants.SEVERITY]
	schema['properties']['status']['enum'] = \
		[i['key'] for i in constants.STATUS]


# Map endpoints to extenders.
# _EXTENDERS['/1/issue/search']['params'] = _1_issue_search_params
# _EXTENDERS['/1/issue/close']['params'] = _1_issue_close_params
# _EXTENDERS['/1/issue/create']['body'] = _1_issue_create_body
# _EXTENDERS['/1/issue/update']['body'] = _1_issue_update_body
