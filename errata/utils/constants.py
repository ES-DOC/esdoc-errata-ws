# -*- coding: utf-8 -*-
"""

.. module:: constants.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - web-service constants.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
# HTTP CORS header.
HTTP_HEADER_Access_Control_Allow_Origin = "Access-Control-Allow-Origin"

# ESDOC GitHub team: errata-publication.
ERRATA_GH_TEAM = 'errata-publication'

# Default endpoint.
DEFAULT_ENDPOINT = r'/1/ops/heartbeat'

# Core facet type - dataset.
FACET_TYPE_DATASET = u'dataset'

# Core facet type - institution ID.
FACET_TYPE_INSTITUTE = u'institute'

# Core facet type - project.
FACET_TYPE_PROJECT = u'project'

# Core facet type - severity.
FACET_TYPE_SEVERITY = u'severity'

# Core facet type - status.
FACET_TYPE_STATUS = u'status'

# Core search facet type set.
CORE_FACET_TYPESET = {
    FACET_TYPE_DATASET,
    FACET_TYPE_INSTITUTE,
    FACET_TYPE_PROJECT,
    FACET_TYPE_SEVERITY,
    FACET_TYPE_STATUS
}

# Issue status - new.
STATUS_NEW = u'new'

# Issue status - on hold.
STATUS_ON_HOLD = u'onhold'

# Issue status - resolved.
STATUS_RESOLVED = u'resolved'

# Issue status - won fix.
STATUS_WONT_FIX = u'wontfix'

# Issue status set.
STATUS = [
    {
        'color': "#00ff00",
        'label': 'New',
        'key': STATUS_NEW
    },
    {
        'color': "#ff9900",
        'label': 'On Hold',
        'key': STATUS_ON_HOLD
    },
    {
        'color': "#0c343d",
        'label': 'Resolved',
        'key': STATUS_RESOLVED
    },
    {
        'color': "#38761d",
        'label': 'Wont Fix',
        'key': STATUS_WONT_FIX
    },
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

# List of issue attributes that cannot be updated.
IMMUTABLE_ISSUE_ATTRIBUTES = [
    'institute',
    'title',
    'project'
    # 'dateCreated'
]

# Ratio of similarity between descriptions of updated and database issue.
DESCRIPTION_CHANGE_RATIO = 20

# PID service task state: complete.
PID_TASK_STATE_COMPLETE = "complete"

# PID service task state: error.
PID_TASK_STATE_ERROR = "error"

# PID service task state: queued awaiting processing.
PID_TASK_STATE_QUEUED = "queued"

# PID service action: insert.
PID_ACTION_INSERT = 'insert'

# PID service action: delete.
PID_ACTION_DELETE = 'delete'
