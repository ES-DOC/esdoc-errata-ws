import pyessv
from pyessv.utils.compat import basestring



# Map of projects to extraction configuration.
_CONFIG = {
	'cmip5': ('.', (
		('wcrp:cmip5:institute', 2),
		('wcrp:cmip5:model', 3),
		('wcrp:cmip5:experiment', 4),
		)),

	'cmip6': ('.', (
		('wcrp:cmip6:institution-id', 2),
		('wcrp:cmip6:source-id', 3),
		('wcrp:cmip6:experiment-id', 4),
		)),

	'cordex': ('.', (
		('wcrp:cordex:institute', 3),
		('wcrp:cordex:rcm-name', 7),
		('wcrp:cordex:experiment', 5),
		)),
}


def extract_facets(project, data):
	"""Extracts terms from a dataset identifer.

    :param str project: Project code.
    :param str|list data: Dataset identifier(s).

    :returns: Set of pyessv terms extracted from dataset identifier.
	:rtype: list

	"""
	seperator, targets = _CONFIG[project]
	facets = []
	identifiers = [data] if isinstance(data, basestring) else data
	for identifier in identifiers:
		parts = identifier.split(seperator)
		facets += ['{}:{}'.format(i, parts[j]) for i, j in targets]

	return [pyessv.load(i) for i in set(facets)]
