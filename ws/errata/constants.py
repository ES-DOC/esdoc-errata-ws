# -*- coding: utf-8 -*-
"""

.. module:: constants.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - web-service constants.

.. moduleauthor:: Atef Benasser <abenasser@ipsl.jussieu.fr>


"""
# Issue state - new.
ISSUE_STATE_NEW = 'new'

# Issue state - on hold.
ISSUE_STATE_ON_HOLD = 'hold'

# Issue state - resolved.
ISSUE_STATE_RESOLVED = 'resolved'

# Issue state - won fix.
ISSUE_STATE_WONT_FIX = 'wontfix'

# Set of supported issue states.
ISSUE_STATES = [
	{
		'color': "#00ff00",
		'label': 'New',
		'key': ISSUE_STATE_NEW
	},
	{
		'color': "#ff9900",
		'label': 'OnHold',
		'key': ISSUE_STATE_ON_HOLD
	},
	{
		'color': "#0c343d",
		'label': 'Resolved',
		'key': ISSUE_STATE_WONT_FIX
	},
	{
		'color': "#38761d",
		'label': 'WontFix',
		'key': ISSUE_STATE_RESOLVED
	},
]
