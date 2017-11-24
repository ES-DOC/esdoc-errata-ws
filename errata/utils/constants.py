# -*- coding: utf-8 -*-
"""

.. module:: utils.constants.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - web-service constants.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
# Default endpoint.
DEFAULT_ENDPOINT = r'/1/ops/heartbeat'

# Ratio of similarity between descriptions of updated and database issue.
DESCRIPTION_CHANGE_RATIO = 20

# ESDOC GitHub team: errata-publication.
ERRATA_GH_TEAM = 'errata-publication'

# Core facet types.
FACET_TYPE_PROJECT = u'project'
FACET_TYPE_SEVERITY = u'severity'
FACET_TYPE_STATUS = u'status'

# HTTP CORS header.
HTTP_HEADER_Access_Control_Allow_Origin = "Access-Control-Allow-Origin"

# List of issue attributes that cannot be updated.
IMMUTABLE_ISSUE_ATTRIBUTES = [
    'title',
    'project'
]

# JSON field names.
JF_DESCRIPTION = u'description'
JF_DATASETS = u'datasets'
JF_MATERIALS = u'materials'
JF_PROJECT = u'project'
JF_SEVERITY = u'severity'
JF_STATUS = u'status'
JF_TITLE = u'title'
JF_UID = u'uid'
JF_URLS = u'urls'

# PID service actions.
PID_ACTION_INSERT = 'insert'
PID_ACTION_DELETE = 'delete'

# PID service task states.
PID_TASK_STATE_COMPLETE = "complete"
PID_TASK_STATE_ERROR = "error"
PID_TASK_STATE_QUEUED = "queued"

# Resource types.
RESOURCE_TYPE_DATASET = 'dataset'
RESOURCE_TYPE_MATERIAL = 'material'
RESOURCE_TYPE_URL = 'url'

# Issue severities.
SEVERITY_LOW = u"low"
SEVERITY_MEDIUM = u"medium"
SEVERITY_HIGH = u"high"
SEVERITY_CRITICAL = u"critical"

# Issue states.
STATUS_NEW = u'new'
STATUS_ON_HOLD = u'onhold'
STATUS_RESOLVED = u'resolved'
STATUS_WONT_FIX = u'wontfix'
