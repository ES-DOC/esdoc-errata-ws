# -*- coding: utf-8 -*-
"""
.. module:: utils.publisher.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Issue publisher helper functions.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import datetime as dt

from errata.utils.config_esg import get_active_project
from errata.utils.constants import PID_ACTION_INSERT
from errata.utils.constants_json import JF_DATE_CLOSED
from errata.utils.constants_json import JF_DATE_CREATED
from errata.utils.constants_json import JF_DATE_UPDATED
from errata.utils.constants_json import JF_DATASETS
from errata.utils.constants_json import JF_DESCRIPTION
from errata.utils.constants_json import JF_INSTITUTE
from errata.utils.constants_json import JF_FACETS
from errata.utils.constants_json import JF_FACET_TYPE_MAP
from errata.utils.constants_json import JF_MATERIALS
from errata.utils.constants_json import JF_PROJECT
from errata.utils.constants_json import JF_SEVERITY
from errata.utils.constants_json import JF_STATUS
from errata.utils.constants_json import JF_TITLE
from errata.utils.constants_json import JF_UID
from errata.utils.constants_json import JF_URLS
from errata.db.models import Issue
from errata.db.models import IssueFacet
from errata.db.models import PIDServiceTask



def create_issue(obj, user_id=u'test-script'):
    """Returns an issue.

    :param dict obj: Over the wire dictionary representation.
    :param str user_id: ID of user responsible for maintaining issue.

    :returns: A 3 member tuple: (issue, facets, pid_tasks).
    :rtype: tuple

    """
    # Issue.
    issue = Issue()
    issue.description = obj[JF_DESCRIPTION].strip()
    issue.institute = obj[JF_INSTITUTE].lower()
    issue.materials = ",".join(obj.get(JF_MATERIALS, []))
    issue.project = obj[JF_PROJECT].lower()
    issue.severity = obj[JF_SEVERITY].lower()
    issue.status = obj[JF_STATUS].lower()
    issue.title = obj[JF_TITLE].strip()
    issue.uid = obj[JF_UID].strip()
    issue.urls = ",".join(obj.get(JF_URLS, []))

    # Issue tracking info.
    issue.date_created = obj.get(JF_DATE_CREATED, dt.datetime.utcnow())
    issue.created_by = user_id

    return issue, _get_facets(issue, obj), _get_pid_tasks(issue, obj)


def update_issue(issue, obj, user_id=u'test-script'):
    """Updates an issue.

    :param db.models.Issue issue: Issue ot be updated.
    :param dict obj: Over the wire dictionary representation.
    :param str user_id: ID of user responsible for maintaining issue.

    """
    # Update issue.
    issue.description = obj[JF_DESCRIPTION].strip()
    issue.materials = ",".join(obj.get(JF_MATERIALS, []))
    issue.severity = obj[JF_SEVERITY].lower()
    issue.status = obj[JF_STATUS].lower()
    issue.title = obj[JF_TITLE].strip()
    issue.urls = ",".join(obj.get(JF_URLS, []))

    # Issue tracking info.
    issue.date_updated = obj.get(JF_DATE_UPDATED, dt.datetime.utcnow())
    issue.updated_by = user_id

    return _get_facets(issue, obj)


def _get_facets(issue, obj):
    """Returns facets extracted from issue data.

    """
    facets = []

    # Core facets.
    for field, facet_type in JF_FACET_TYPE_MAP.items():
        facet_values =  obj[field]
        if not isinstance(facet_values, list):
            facet_values = [facet_values]
        for facet_value in facet_values:
            facet = IssueFacet()
            facet.project = issue.project
            facet.issue_uid = issue.uid
            facet.facet_type = facet_type
            facet.facet_value = facet_value
            facets.append(facet)

    # Project specific facets.
    for facet_type, facet_values in obj[JF_FACETS].items():
        for facet_value in facet_values:
            facet = IssueFacet()
            facet.project = issue.project
            facet.issue_uid = issue.uid
            facet.facet_type = facet_type
            facet.facet_value = facet_value
            facets.append(facet)

    return facets


def _get_pid_tasks(issue, obj):
    """Returns PID service tasks extracted from issue data.

    """
    pid_tasks = []
    project_conf = get_active_project(obj[JF_PROJECT])
    if project_conf['is_pid_client']:
        for identifier in obj[JF_DATASETS]:
            task = PIDServiceTask()
            task.action = PID_ACTION_INSERT
            task.issue_uid = issue.uid
            task.dataset_id = identifier
            pid_tasks.append(task)

    return pid_tasks
