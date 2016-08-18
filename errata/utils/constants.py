# -*- coding: utf-8 -*-
"""

.. module:: constants.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - web-service constants.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import json
import os



# Issue workflow state - new.
WORKFLOW_NEW = u'new'

# Issue workflow state - on hold.
WORKFLOW_ON_HOLD = u'onhold'

# Issue workflow state - resolved.
WORKFLOW_RESOLVED = u'resolved'

# Issue workflow state - won fix.
WORKFLOW_WONT_FIX = u'wontfix'

# Issue workflow state set.
WORKFLOW = [
	{
		'color': "#00ff00",
		'label': 'New',
		'key': WORKFLOW_NEW
	},
	{
		'color': "#ff9900",
		'label': 'On Hold',
		'key': WORKFLOW_ON_HOLD
	},
	{
		'color': "#0c343d",
		'label': 'Resolved',
		'key': WORKFLOW_RESOLVED
	},
	{
		'color': "#38761d",
		'label': 'Wont Fix',
		'key': WORKFLOW_WONT_FIX
	},
]

# Issue state - open.
STATE_OPEN = u"open"

# Issue state - closed.
STATE_CLOSED = u"closed"

# Issue states set.
STATE = [
	{
		'color': "#00ff00",
		'label': 'Open',
		'key': STATE_OPEN
	},
	{
		'color': "#ff9900",
		'label': 'Closed',
		'key': STATE_CLOSED
	}
]

# Issue severity - low.
SEVERITY_LOW = u"low"

# Issue severity - medium.
SEVERITY_MEDIUM = u"medium"

# Issue severity - high.
SEVERITY_HIGH = u"high"

# Issue severity - critical.
SEVERITY_CRITICAL = u"critical"

# Issue severity level set.
SEVERITY = [
	{
		'color': "#e6b8af",
		'label': 'Low',
		'key': SEVERITY_LOW,
		'sortOrdinal': 0
	},
	{
		'color': "#dd7e6b",
		'label': 'Medium',
		'key': SEVERITY_MEDIUM,
		'sortOrdinal': 1
	},
	{
		'color': "#cc4125",
		'label': 'High',
		'key': SEVERITY_HIGH,
		'sortOrdinal': 2
	},
	{
		'color': "#a61c00",
		'label': 'Critical',
		'key': SEVERITY_CRITICAL,
		'sortOrdinal': 3
	},
]

# TODO - leverage pyessv
# Project - cmip5.
PROJECT_CMIP5 = u"cmip5"

# Project - cmip6.
PROJECT_CMIP6 = u"cmip6"

# Project - test.
PROJECT_TEST = u"test"

# Project - all.
PROJECT = [
	{
	    'key': PROJECT_CMIP5,
	    'label': u"CMIP5"
	},
	{
	    'key': PROJECT_CMIP6,
	    'label': u"CMIP6"
	},
	{
	    'key': PROJECT_TEST,
	    'label': u"TEST"
	}
]


# TODO - leverage pyessv
# Institute - BADC.
INSTITUTE_BADC = u"badc"

# Institute - DKRZ.
INSTITUTE_DKRZ = u"dkrz"

# Institute - IPSL.
INSTITUTE_IPSL = u"ipsl"

# Institute - all.
INSTITUTE = [
	{
	    'key': INSTITUTE_BADC,
	    'label': u"BADC"
	},
	{
	    'key': INSTITUTE_DKRZ,
	    'label': u"DKRZ"
	},
	{
	    'key': INSTITUTE_IPSL,
	    'label': u"IPSL"
	}
]

# List of issue attributes that cannot be updated.
IMMUTABLE_ISSUE_ATTRIBUTES = [
	'title',
	'project',
	'institute',
	# 'dateCreated'
	]

def _get_json_schema(name):
	"""Returns a JSON schema.

	"""
	fpath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemas")
	fpath = os.path.join(fpath, "{}.json".format(name))
	with open(fpath, 'r') as fstream:
		return json.loads(fstream.read())

# Map of actions to json schemas.
JSON_SCHEMAS = {i: _get_json_schema(i) for i in ['create', 'update']}

# Extend CV's embedded within JSON schemas.
JSON_SCHEMAS['create']['properties']['institute']['enum'] = [i['key'] for i in INSTITUTE]
JSON_SCHEMAS['update']['properties']['institute']['enum'] = [i['key'] for i in INSTITUTE]
JSON_SCHEMAS['create']['properties']['project']['enum'] = [i['key'] for i in PROJECT]
JSON_SCHEMAS['update']['properties']['project']['enum'] = [i['key'] for i in PROJECT]

# Ratio of similarity between descriptions of updated and database issue.
DESCRIPTION_CHANGE_RATIO = 20
