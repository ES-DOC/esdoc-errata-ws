# -*- coding: utf-8 -*-
"""
.. module:: handlers.retrieve.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - retrieve issue endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from errata.db.dao_validator import validate_delete_facets
from errata.db.dao_validator import validate_get_facets
from errata.db.dao_validator import validate_get_issue
from errata.db.dao_validator import validate_get_issues
from errata.db.dao_validator import validate_get_issues_by_facet
from errata.db.models import Issue
from errata.db.models import IssueFacet
from errata.db.models import PIDServiceTask
from errata.db.session import query
from errata.db.session import raw_query
from errata.db.utils import text_filter
from errata.db.utils import as_date_string
from errata.utils import constants
from errata.utils.constants import PID_ACTION_DELETE
from errata.utils.validation import validate
from sqlalchemy import or_



@validate(validate_delete_facets)
def delete_facets(uid):
    """Deletes search facets associated with an issue.

    :param str uid: Issue unique identifier.

    """
    qry = query(IssueFacet)
    qry = qry.filter(IssueFacet.issue_uid == uid)

    qry.delete()


@validate(validate_get_facets)
def get_facets(facet_type=None, issue_uid=None):
    """Returns set of facets.

    :param str facet_type: Type of facet to filter result set by.
    :param str issue_uid: Unique issue identifier.

    :returns: Matching facets.
    :rtype: list

    """
    if issue_uid:
        qry = raw_query(
            IssueFacet.facet_value,
            IssueFacet.facet_type,
            IssueFacet.issue_uid
            )
    else:
        qry = raw_query(
            IssueFacet.facet_value,
            IssueFacet.facet_type
            )
    if issue_uid is not None:
        qry = text_filter(qry, IssueFacet.issue_uid, issue_uid)
    if facet_type is not None:
        qry = qry.filter(IssueFacet.facet_type == facet_type)
    qry = qry.distinct()

    return qry.all()


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
def get_issues(criteria):
    """Returns collection of matching issues.

    :param list criteria: Collection of 2 member tuples: (facet-type, facet-value).

    :returns: List of matching issues.
    :rtype: list

    """
    qry = raw_query(
        Issue.project,
        Issue.institute,
        Issue.uid,
        Issue.title,
        Issue.severity,
        Issue.status,
        as_date_string(Issue.date_created),
        as_date_string(Issue.date_closed),
        as_date_string(Issue.date_updated)
        )

    for facet_type, facet_value in criteria:
        sub_qry = query(IssueFacet.issue_uid)
        sub_qry = sub_qry.filter(IssueFacet.facet_type == facet_type)
        sub_qry = text_filter(sub_qry, IssueFacet.facet_value, facet_value)
        qry = qry.filter(Issue.uid.in_(sub_qry))

    return qry.all()


@validate(validate_get_project_facets)
def get_project_facets(excluded_types=[]):
    """Returns collection of facets.

    :param list excluded_types: Facets to be excluded from search.

    :returns: Matching facets.
    :rtype: list

    """
    qry = raw_query(
        IssueFacet.project,
        IssueFacet.facet_type,
        IssueFacet.facet_value
        )
    for facet_type in excluded_types:
        qry = qry.filter(IssueFacet.facet_type != facet_type)
    qry = qry.distinct()

    return qry.all()


def get_all_issues():
    """Returns all issues within database.

    """
    return query(Issue).all()


@validate(validate_get_issues_by_facet)
def get_issues_by_facet(facet_value, facet_type):
    """Returns issues associated with a facet.

    :param str facet_value: A facet value.
    :param str facet_type: Type of issue facet, e.g. dataset.

    :returns: Matching issues.
    :rtype: list

    """
    qry = raw_query(IssueFacet.issue_uid)
    qry = text_filter(qry, IssueFacet.facet_value, facet_value)
    qry = qry.filter(IssueFacet.facet_type == facet_type)

    return sorted([i[0] for i in qry.all()])


def get_pid_service_tasks():
    """Returns pid service tasks awaiting processing.

    """
    qry = query(PIDServiceTask)
    qry = qry.filter(or_(PIDServiceTask.status == constants.PID_TASK_STATE_QUEUED,
                         PIDServiceTask.status == constants.PID_TASK_STATE_ERROR))
    qry = qry.order_by(PIDServiceTask.timestamp.desc())

    return qry.all()
