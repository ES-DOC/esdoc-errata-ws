import collections

from errata_ws.schemas import loader



# Cached store of loaded schemas.
_store = collections.defaultdict(dict)



def init(endpoints):
	"""Initializes cache from schemas upon file system.

	:param dict endpoints: Map of application endpoints.

	"""
	for endpoint in endpoints:
		for typeof in {'body', 'params', 'headers'}:
			_store[typeof][endpoint] = loader.load(typeof, endpoint)


def get_schema(typeof, endpoint):
	"""Gets a schema from cache.

	"""
	return _store[typeof][endpoint]
