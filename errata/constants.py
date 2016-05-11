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
WORKFLOW_ON_HOLD = 'hold'

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
		'label': 'OnHold',
		'key': WORKFLOW_ON_HOLD
	},
	{
		'color': "#0c343d",
		'label': 'Resolved',
		'key': WORKFLOW_WONT_FIX
	},
	{
		'color': "#38761d",
		'label': 'WontFix',
		'key': WORKFLOW_RESOLVED
	},
]

# Issue status - open.
STATUS_OPEN = "open"

# Issue status - closed.
STATUS_CLOSED = "closed"

# Issue states set.
STATUS = [
	{
		'color': "#00ff00",
		'label': 'Open',
		'key': STATUS_OPEN
	},
	{
		'color': "#ff9900",
		'label': 'Closed',
		'key': STATUS_CLOSED
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
		'key': SEVERITY_LOW
	},
	{
		'color': "#ff9900",
		'label': 'Medium',
		'key': SEVERITY_MEDIUM
	},
	{
		'color': "#0c343d",
		'label': 'High',
		'key': SEVERITY_HIGH
	},
	{
		'color': "#38761d",
		'label': 'Critical',
		'key': SEVERITY_CRITICAL
	},
]
