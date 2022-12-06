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

# Core facet types.
FACET_TYPE_PROJECT = u'project'
FACET_TYPE_SEVERITY = u'severity'
FACET_TYPE_STATUS = u'status'

# HTTP CORS header.
HTTP_HEADER_Access_Control_Allow_Origin = "Access-Control-Allow-Origin"

# Processing error HTTP response codes.
HTTP_RESPONSE_BAD_REQUEST_ERROR = 400
HTTP_RESPONSE_SERVER_ERROR = 500

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

# List of issue attributes that cannot be updated.
ISSUE_IMMUTABLE_ATTRIBUTES = [
    'title',
    'project'
]

# Issue moderation states.
ISSUE_MODERATION_ACCEPTED = "accepted"
ISSUE_MODERATION_IN_REVIEW = "in-review"
ISSUE_MODERATION_NOT_REQUIRED = "not-required"
ISSUE_MODERATION_REJECTED = "rejected"

# Resource types.
ISSUE_RESOURCE_DATASET = 'dataset'
ISSUE_RESOURCE_MATERIAL = 'material'
ISSUE_RESOURCE_URL = 'url'

# Issue severities.
ISSUE_SEVERITY_LOW = u"low"
ISSUE_SEVERITY_MEDIUM = u"medium"
ISSUE_SEVERITY_HIGH = u"high"
ISSUE_SEVERITY_CRITICAL = u"critical"

# Issue states.
ISSUE_STATUS_NEW = u'new'
ISSUE_STATUS_ON_HOLD = u'onhold'
ISSUE_STATUS_RESOLVED = u'resolved'
ISSUE_STATUS_WONT_FIX = u'wontfix'

# PID service actions.
PID_ACTION_INSERT = 'insert'
PID_ACTION_DELETE = 'delete'

# PID service task states.
PID_TASK_STATE_COMPLETE = "complete"
PID_TASK_STATE_ERROR = "error"
PID_TASK_STATE_QUEUED = "queued"

# User roles.
USER_ROLE_ANONYMOUS="anonymous"
USER_ROLE_AUTHOR="author"
USER_ROLE_MODERATOR="moderator"

# regex
VERSION_REGEX = r'(?P<version_string>(\.v|#)\d+)$'
