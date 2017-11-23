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


# Core facet type - project.
FACET_TYPE_PROJECT = u'project'

# Core facet type - severity.
FACET_TYPE_SEVERITY = u'severity'

# Core facet type - status.
FACET_TYPE_STATUS = u'status'

# Core search facet type set.
CORE_FACET_TYPESET = {
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
STATUS = {
    STATUS_NEW,
    STATUS_ON_HOLD,
    STATUS_RESOLVED,
    STATUS_WONT_FIX
}

# Issue severity - low.
SEVERITY_LOW = u"low"

# Issue severity - medium.
SEVERITY_MEDIUM = u"medium"

# Issue severity - high.
SEVERITY_HIGH = u"high"

# Issue severity - critical.
SEVERITY_CRITICAL = u"critical"

# Issue severity level set.
SEVERITY = {
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    SEVERITY_HIGH,
    SEVERITY_CRITICAL
}

# List of issue attributes that cannot be updated.
IMMUTABLE_ISSUE_ATTRIBUTES = [
    'institute',
    'title',
    'project'
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

# Resource type: dataset.
RESOURCE_TYPE_DATASET = 'dataset'

# Resource type: material.
RESOURCE_TYPE_MATERIAL = 'material'

# Resource type: url.
RESOURCE_TYPE_URL = 'url'

# Resouce typeset.
RESOURCE_TYPE = {
    RESOURCE_TYPE_DATASET,
    RESOURCE_TYPE_MATERIAL,
    RESOURCE_TYPE_URL
}
