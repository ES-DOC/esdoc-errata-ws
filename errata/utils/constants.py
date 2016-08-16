# -*- coding: utf-8 -*-
"""

.. module:: constants.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - web-service constants.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import os

# Issue workflow state - new.
WORKFLOW_NEW = 'new'

# Issue workflow state - on hold.
WORKFLOW_ON_HOLD = 'onhold'

# Issue workflow state - resolved.
WORKFLOW_RESOLVED = 'resolved'

# Issue workflow state - won fix.
WORKFLOW_WONT_FIX = 'wontfix'

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
STATE_OPEN = "open"

# Issue state - closed.
STATE_CLOSED = "closed"

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
SEVERITY_LOW = "low"

# Issue severity - medium.
SEVERITY_MEDIUM = "medium"

# Issue severity - high.
SEVERITY_HIGH = "high"

# Issue severity - critical.
SEVERITY_CRITICAL = "critical"

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
PROJECT_CMIP5 = "cmip5"

# Project - cmip6.
PROJECT_CMIP6 = "cmip6"

# Project - all.
PROJECT = {
	"TEST",
	PROJECT_CMIP5,
	PROJECT_CMIP6
}

# TODO - leverage pyessv
# Institute - IPSL.
INSTITUTE_IPSL = "ipsl"

# Institute - DKRZ.
INSTITUTE_DKRZ = "dkrz"

# Institute - BADC.
INSTITUTE_BADC = "badc"

# Institute - all.
INSTITUTE = {
	INSTITUTE_IPSL,
	INSTITUTE_DKRZ,
	INSTITUTE_BADC
}

# List of issue attributes that cannot be updated.
IMMUTABLE_ISSUE_ATTRIBUTES = [
	'title',
	'project',
	'institute',
	# 'date_created'
	]

def _get_json_schema(name):
	"""Returns a JSON schema.

	"""
	fpath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemas")
	fpath = os.path.join(fpath, "{}.json".format(name))
	with open(fpath, 'r') as fstream:
		return fstream.read()

# Map of actions to json schemas.
JSON_SCHEMAS = {i: _get_json_schema(i) for i in ['create', 'retrieve', 'update']}

# Ratio of similarity between descriptions of updated and database issue.
DESCRIPTION_CHANGE_RATIO = 20
