# -*- coding: utf-8 -*-
"""
.. module:: handlers.retrieve.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - retrieve issue endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from sqlalchemy import or_

from errata.db.dao_validator import validate_delete_facets
from errata.db.dao_validator import validate_delete_resources
from errata.db.dao_validator import validate_get_datasets
from errata.db.dao_validator import validate_get_issue
from errata.db.dao_validator import validate_get_issues
from errata.db.dao_validator import validate_get_resources
from errata.db.models import Issue
from errata.db.models import IssueFacet
from errata.db.models import IssueResource
from errata.db.models import PIDServiceTask
from errata.db.session import query
from errata.db.session import raw_query
from errata.db.utils import as_date_string
from errata.db.utils import text_filter
from errata.utils.constants import *
from errata.utils.validation import validate



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
    qry = qry.filter(IssueResource.resource_type == RESOURCE_TYPE_DATASET)
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


@validate(validate_get_issues)
def get_issues(criteria=None):
    """Returns collection of matching issues.

    :param dict criteria: Map of criteria facet-types to facet-values.

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
        as_date_string(Issue.updated_date)
        )

    print 444, criteria

    # for facet_type, facet_values in criteria.items():
    #     for facet_value in facet_values:
    #         sub_qry = query(IssueFacet.issue_uid)
    #         sub_qry = sub_qry.filter(IssueFacet.facet_type == facet_type)
    #         sub_qry = text_filter(sub_qry, IssueFacet.facet_value, facet_value)
    #         qry = qry.filter(Issue.uid.in_(sub_qry))

    return qry.all()


def get_pid_service_tasks():
    """Returns pid service tasks awaiting processing.

    """
    qry = query(PIDServiceTask)
    qry = qry.filter(or_(PIDServiceTask.status == PID_TASK_STATE_QUEUED,
                         PIDServiceTask.status == PID_TASK_STATE_ERROR))
    qry = qry.order_by(PIDServiceTask.timestamp.desc())

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
