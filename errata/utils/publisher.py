import pyessv

import datetime as dt

from errata.utils.constants import *
from errata.utils.facet_extractor import extract_facets
from errata.db.models import Issue
from errata.db.models import IssueFacet
from errata.db.models import IssueResource
from errata.db.models import PIDServiceTask



def create_issue(obj, user_id):
    """Returns set of db entities created when processing a new issue.

    :param obj: Over the wire dictionary representation (i.e. coming from client).
    :param user_id: ID of an authenticated user (publisher or moderator).
    :returns: List of db entities.

    """
    # Issue - core fields.
    issue = Issue()
    issue.description = obj[JF_DESCRIPTION].strip()
    issue.moderation_status = ISSUE_MODERATION_NOT_REQUIRED
    issue.project = obj[JF_PROJECT].lower()
    issue.institute = get_institute(obj)
    issue.severity = obj[JF_SEVERITY].lower()
    issue.status = obj[JF_STATUS].lower()
    issue.title = obj[JF_TITLE].strip()
    issue.uid = obj[JF_UID].strip()

    # Issue - tracking info.
    issue.created_by = user_id
    issue.created_date = dt.datetime.utcnow()

    # Return issue + associated entities.
    return [issue] + _get_resources(issue, obj) + _get_facets(issue, obj) + _get_pid_tasks(issue, obj)


def get_proposed_issue_entities(obj, user_email):
    """Returns set of db entities created when processing a new issue.

    :param obj: Over the wire dictionary representation (i.e. coming from client).
    :param user_email: Email of anonymous user.
    :returns: List of db entities.

    """
    # Issue - core fields.
    issue = Issue()
    issue.description = obj[JF_DESCRIPTION].strip()
    issue.moderation_status = ISSUE_MODERATION_IN_REVIEW
    issue.project = obj[JF_PROJECT].lower()
    issue.institute = get_institute(obj)
    issue.severity = obj[JF_SEVERITY].lower()
    issue.status = obj[JF_STATUS].lower()
    issue.title = obj[JF_TITLE].strip()
    issue.uid = obj[JF_UID].strip()

    # Issue - tracking info.
    issue.created_by = user_email
    issue.created_date = dt.datetime.utcnow()

    return \
        [issue] + \
        _get_resources(issue, obj) + \
        _get_facets(issue, obj) + \
        _get_pid_tasks(issue, obj)


def update_issue(issue, obj, user_id):
    """Updates an issue.

    :param issue: Issue to be updated.
    :param obj: Over the wire dictionary representation (i.e. coming from client).
    :param user_id: ID of an authenticated user (publisher or moderator).
    :returns: List of db entities.

    """
    # Issue - core fields.
    issue.description = obj[JF_DESCRIPTION].strip()
    issue.severity = obj[JF_SEVERITY].lower()
    issue.status = obj[JF_STATUS].lower()
    issue.title = obj[JF_TITLE].strip()

    # Issue - tracking info.
    issue.updated_by = user_id
    issue.updated_date = dt.datetime.utcnow()

    return _get_resources(issue, obj) + _get_facets(issue, obj)


def close_issue(issue, status, user_id):
    """Updates an issue.

    :param issue: Issue to be closed.
    :param status: Issue status.
    :param user_id: ID of an authenticated user (publisher or moderator).

    """
    # Issue - core fields.
    issue.status = status

    # Issue - tracking info.
    issue.closed_by = user_id
    issue.closed_date = dt.datetime.utcnow()


def get_institute(obj):
    """Returns insitiute identifier from issue data.

    """
    return get_institutes(obj)[0].canonical_name


def get_institutes(obj):
    """Returns insitiute identifiers from issue data.

    """
    terms = pyessv.parse_dataset_identifers(obj[JF_PROJECT], obj[JF_DATASETS])

    return [i for i in terms if i.collection.canonical_name in ('institute', 'institution-id')]


def _get_resources(issue, obj):
    """Returns resources extracted from issue data.

    """
    resources = []
    for typeof, locations in (
        (ISSUE_RESOURCE_DATASET, obj[JF_DATASETS]),
        (ISSUE_RESOURCE_MATERIAL, obj.get(JF_MATERIALS, [])),
        (ISSUE_RESOURCE_URL, obj.get(JF_URLS, [])),
        ):
        for location in locations:
            resource = IssueResource()
            resource.issue_uid = issue.uid
            resource.resource_type = typeof
            resource.resource_location = location
            resources.append(resource)

    return resources


def _get_facets(issue, obj):
    """Returns facets extracted from issue data.

    """
    facets = []

    # Core facets.
    for facet_type in {
            FACET_TYPE_PROJECT,
            FACET_TYPE_SEVERITY,
            FACET_TYPE_STATUS
        }:
        facet = IssueFacet()
        facet.project = issue.project
        facet.issue_uid = issue.uid
        facet.facet_type = u'esdoc:errata:{}'.format(facet_type)
        facet.facet_value = getattr(issue, facet_type).lower()
        facets.append(facet)

    # Project specific facets.
    for term in pyessv.parse_dataset_identifers(issue.project, obj[JF_DATASETS]):
        facet = IssueFacet()
        facet.project = issue.project
        facet.issue_uid = issue.uid
        facet.facet_type = term.collection.namespace
        facet.facet_value = term.canonical_name
        facets.append(facet)

    return facets


def _get_pid_tasks(issue, obj):
    """Returns PID service tasks extracted from issue data.

    """
    pid_tasks = []
    project = pyessv.load('esdoc:errata:project:{}'.format(issue.project))
    if project.data['is_pid_client'] == True:
        for identifier in obj[JF_DATASETS]:
            task = PIDServiceTask()
            task.action = PID_ACTION_INSERT
            task.issue_uid = issue.uid
            task.dataset_id = identifier
            pid_tasks.append(task)

    return pid_tasks
