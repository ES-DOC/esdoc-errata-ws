import collections

from errata_ws.utils import constants


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
