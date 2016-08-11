# -*- coding: utf-8 -*-

"""
.. module:: errata.issue_manager.constants.py
   :platform: Unix
   :synopsis: Constants used in this module for better readability of code.

.. moduleauthor:: Guillaume Levavasseur <glipsl@ipsl.jussieu.fr>


"""
import os



# List of keys that cannot be updated
IMMUTABLE_KEYS = [
	'title',
	'project',
	'institute',
	'date_created'
	]

def _get_json_schema(name):
	"""Returns a JSON schema.

	"""
	fpath = os.path.join(os.path.dirname(__file__), "schemas")
	fpath = os.path.join(fpath, "{}.json".format(name))
	with open(fpath, 'r') as fstream:
		return fstream.read()

# Map of actions to json schemas.
JSON_SCHEMAS = {i: _get_json_schema(i) for i in ['create', 'retrieve', 'update']}

# Ratio of similarity between descriptions of updated and database issue.
RATIO = 20
