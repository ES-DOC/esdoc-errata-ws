from sqlalchemy import or_

from errata_ws.db.dao_validator import validate_delete_facets
from errata_ws.db.dao_validator import validate_delete_resources
from errata_ws.db.dao_validator import validate_get_datasets
from errata_ws.db.dao_validator import validate_get_issue
from errata_ws.db.dao_validator import validate_get_issues
from errata_ws.db.dao_validator import validate_get_resources
from errata_ws.db.models import Issue
from errata_ws.db.models import IssueFacet
from errata_ws.db.models import IssueResource
from errata_ws.db.models import PIDServiceTask
from errata_ws.db.session import query
from errata_ws.db.session import raw_query
from errata_ws.db.utils import as_date_string
from errata_ws.db.utils import text_filter
from errata_ws.utils import constants
from errata_ws.utils.constants import *
from errata_ws.utils.validation import validate


@validate(validate_delete_facets)
def delete_facets(uid):
    """Deletes search facets associated with an issue.

    :param str uid: Issue unique identifier.

    """
    qry = query(IssueFacet)
    qry = qry.filter(IssueFacet.issue_uid == uid)

    qry.delete()


@validate(validate_delete_resources)
def delete_resources(uid):
    """Deletes resources associated with an issue.

    :param str uid: Issue unique identifier.

    """
    qry = query(IssueResource)
    qry = qry.filter(IssueResource.issue_uid == uid)

    qry.delete()


@validate(validate_get_datasets)
def get_datasets(issue_uid):
    """Returns set of issue datasets.

    :param str issue_uid: Unique issue identifier.

    :returns: Related resource collection.
    :rtype: list

    """
    qry = query(IssueResource)
    qry = qry.filter(IssueResource.resource_type == ISSUE_RESOURCE_DATASET)
    if issue_uid is not None:
        qry = text_filter(qry, IssueResource.issue_uid, issue_uid)

    return set([i.resource_location for i in qry.all()])


@validate(validate_get_issue)
def get_issue(uid):
    """Returns an issue.

    :param str uid: Issue unique identifier.

    :returns: First matching issue.
    :rtype: db.models.Issue

    """
    qry = query(Issue)
    qry = text_filter(qry, Issue.uid, uid)

    return qry.first()


def get_titles():
    """Returns list of all issue titles in db

    :rtype: list

    """
    qry = raw_query(Issue.title)
    
    return [x[0] for x in qry.all()]


def get_descriptions():
    """Returns list of all issue descriptions in db

    :rtype: list

    """
    qry = raw_query(Issue.description, Issue.uid)
    
    return [(x[0], x[1])for x in qry.all()]


@validate(validate_get_issues)
def get_issues(criteria=None):
    """Returns collection of matching issues.

    :param list criteria: Map of criteria facet-types to facet-values.

    :returns: List of matching issues.
    :rtype: list

    """
    if criteria is None:
        return query(Issue).all()

    qry = raw_query(
        Issue.project,
        Issue.institute,
        Issue.uid,
        Issue.title,
        Issue.severity,
        Issue.status,
        as_date_string(Issue.created_date),
        as_date_string(Issue.closed_date),
        as_date_string(Issue.updated_date),
        Issue.moderation_status
        )

    qry = qry.filter(Issue.moderation_status.in_([
        constants.ISSUE_MODERATION_ACCEPTED,
        constants.ISSUE_MODERATION_NOT_REQUIRED
        ]))

    for item in criteria:
        sub_qry = query(IssueFacet.issue_uid)
        sub_qry = sub_qry.filter(IssueFacet.facet_type == ':'.join(item.split(':')[0:3]))
        sub_qry = text_filter(sub_qry, IssueFacet.facet_value, item.split(':')[-1])
        qry = qry.filter(Issue.uid.in_(sub_qry))
    
    return qry.all()


@validate(validate_get_issues)
def get_issues_for_moderation(criteria):
    """Returns collection of matching issues.

    :param list criteria: Map of criteria facet-types to facet-values.

    :returns: List of matching issues.
    :rtype: list

    """
    if criteria is None:
        return query(Issue).all()

    qry = raw_query(
        Issue.project,
        Issue.institute,
        Issue.uid,
        Issue.title,
        Issue.severity,
        Issue.status,
        as_date_string(Issue.created_date),
        as_date_string(Issue.closed_date),
        as_date_string(Issue.updated_date),
        Issue.moderation_status
        )

    for item in criteria:
        sub_qry = query(IssueFacet.issue_uid)
        sub_qry = sub_qry.filter(IssueFacet.facet_type == ':'.join(item.split(':')[0:3]))
        sub_qry = text_filter(sub_qry, IssueFacet.facet_value, item.split(':')[-1])
        qry = qry.filter(Issue.uid.in_(sub_qry))

    return qry.all()


def get_facets(issue_uid=None):
    """Returns collection of facets.

    :param str issue_uid: Unique issue identifier.

    :returns: Set of facets from database.
    :rtype: list

    """
    qry = query(IssueFacet)
    if issue_uid is not None:
        qry = text_filter(qry, IssueFacet.issue_uid, issue_uid)

    return qry.all()


def get_pid_tasks(criteria=None):
    """Returns pid service tasks awaiting processing.

    """
    qry = query(PIDServiceTask)
    if criteria is None:
        qry = qry.filter(or_(PIDServiceTask.status == PID_TASK_STATE_QUEUED,
                             PIDServiceTask.status == PID_TASK_STATE_ERROR))
    else:
        for field, value in criteria:
            if field == 'project':
                qry = qry.filter(PIDServiceTask.dataset_id.like('{}.%'.format(value)))
            else:
                qry = qry.filter(getattr(PIDServiceTask, field) == value)
    qry = qry.order_by(PIDServiceTask.timestamp.asc())

    return qry.all()


def get_project_facets():
    """Returns collection of facets.

    :returns: Set of facets from database.
    :rtype: list

    """
    qry = raw_query(
        IssueFacet.facet_type,
        IssueFacet.facet_value
        )
    qry = qry.distinct()

    return sorted(['{}:{}'.format(i[0], i[1]) for i in qry.all()])


@validate(validate_get_resources)
def get_resources(issue_uid=None):
    """Returns set of issue resources.

    :param str issue_uid: Unique issue identifier.

    :returns: Related resource collection.
    :rtype: list

    """
    qry = query(IssueResource)
    if issue_uid is not None:
        qry = text_filter(qry, IssueResource.issue_uid, issue_uid)

    return qry.all()
