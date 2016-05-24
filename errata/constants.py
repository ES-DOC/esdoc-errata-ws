# -*- coding: utf-8 -*-
"""

.. module:: constants.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - web-service constants.

.. moduleauthor:: Atef Benasser <abenasser@ipsl.jussieu.fr>


"""
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
		'color': "#00ff00",
		'label': 'Low',
		'key': SEVERITY_LOW,
		'sortOrdinal': 0
	},
	{
		'color': "#ff9900",
		'label': 'Medium',
		'key': SEVERITY_MEDIUM,
		'sortOrdinal': 1
	},
	{
		'color': "#0c343d",
		'label': 'High',
		'key': SEVERITY_HIGH,
		'sortOrdinal': 2
	},
	{
		'color': "#38761d",
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

