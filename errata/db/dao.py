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
from errata.utils.validation import validate
from sqlalchemy import or_



@validate(validate_delete_facets)
def delete_facets(issue_uid, facet_type=None):
    """Deletes search facets associated with an issue.

    :param str issue_uid: Issue unique identifier.
    :param str facet_type: Type of issue facet, e.g. dataset.

    """
    qry = query(IssueFacet)
    qry = qry.filter(IssueFacet.issue_uid == issue_uid)
    if facet_type is not None:
        qry = qry.filter(IssueFacet.facet_type == facet_type)

    qry.delete()


@validate(validate_get_facets)
def get_facets(facet_type=None, include_issue_uid=True, issue_uid=None):
    """Returns set of facets.

    :param str facet_type: Type of facet to filter result set by.
    :param bool include_issue_uid: Flag indicating whether issue identifier will be included in result set.
    :param str issue_uid: Unique issue identifier.

    :returns: Matching facets.
    :rtype: list

    """
    if issue_uid or include_issue_uid:
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
def get_issues(
    experiment=None,
    institute=None,
    project=None,
    model=None,
    severity=None,
    status=None,
    variable=None,
    retrieve_all=False
    ):
    """Returns issues that match the passed filters.

    :param str experiment: Experiment associated with the issue, e.g. decadal1970.
    :param str institute: Institute associated with the issue, e.g. ipsl.
    :param str model: Model associated with the issue, e.g. ipsl-cm6a-lr.
    :param str project: Project associated with the issue, e.g. cmip6.
    :param str severity: Issue severity, e.g. low.
    :param str status: Issue status, e.g. hold.
    :param str variable: Variable associated with the issue, e.g. tos.
    :param bool retrieve_all: Flag indicating whether to simply return all issues.

    :returns: List of matching issues.
    :rtype: list

    """
    if retrieve_all:
        return query(Issue).all()

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

    criteria = {
        (experiment, constants.FACET_TYPE_EXPERIMENT),
        (institute, constants.FACET_TYPE_INSTITUTE),
        (project, constants.FACET_TYPE_PROJECT),
        (model, constants.FACET_TYPE_MODEL),
        (severity, constants.FACET_TYPE_SEVERITY),
        (status, constants.FACET_TYPE_STATUS),
        (variable, constants.FACET_TYPE_VARIABLE)
    }

    for facet_value, facet_type in [i for i in criteria if i[0] is not None]:
        sub_qry = query(IssueFacet.issue_uid)
        sub_qry = sub_qry.filter(IssueFacet.facet_type == facet_type)
        sub_qry = text_filter(sub_qry, IssueFacet.facet_value, facet_value)
        qry = qry.filter(Issue.uid.in_(sub_qry))

    return qry.all()


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
