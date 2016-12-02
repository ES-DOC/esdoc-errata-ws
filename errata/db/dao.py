# -*- coding: utf-8 -*-
"""
.. module:: handlers.retrieve.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - retrieve issue endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from errata.db.dao_validator import validate_delete_facets
from errata.db.dao_validator import validate_get_issues_by_facet
from errata.db.dao_validator import validate_get_issue
from errata.db.dao_validator import validate_get_issues
from errata.db.dao_validator import validate_get_facets
from errata.db.models import Issue
from errata.db.models import IssueFacet
from errata.db.session import query
from errata.db.session import raw_query
from errata.db.utils import text_filter
from errata.db.utils import as_date_string
from errata.utils import constants
from errata.utils.validation import validate



@validate(validate_delete_facets)
def delete_facets(issue_uid, facet_type=None):
    """Deletes search facets associated with an issue.

    :param str issue_uid: Issue unique identifier.
    :param str facet_type: Type of issue facet, e.g. dataset.

    """
    qry = query(IssueFacet)
    qry = qry.filter(IssueFacet.issue_uid == issue_uid)
    if facet_type:
        qry = qry.filter(IssueFacet.facet_type == facet_type)

    qry.delete()


@validate(validate_get_facets)
def get_facets(issue_uid=None):
    """Returns facets associated with an issue.

    :param str issue_uid: Issue unique identifier.

    :returns: Matching issues.
    :rtype: list

    """
    if issue_uid:
        qry = raw_query(
            IssueFacet.issue_uid,
            IssueFacet.facet_id,
            IssueFacet.facet_type
            )
        qry = text_filter(qry, IssueFacet.issue_uid, issue_uid)

        return qry.all()

    else:
        qry = raw_query(
            IssueFacet.facet_id,
            IssueFacet.facet_type
            )
        qry = qry.filter(IssueFacet.facet_type != constants.FACET_TYPE_DATASET)

        return list(set(qry.all()))


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
    model=None,
    project=None,
    severity=None,
    status=None,
    variable=None,
    subset=True
    ):
    """Returns issues that match the passed filters.

    :param str experiment: Experiment associated with the issue, e.g. decadal1970.
    :param str institute: Institute associated with the issue, e.g. ipsl.
    :param str model: Model associated with the issue, e.g. ipsl-cm6a-lr.
    :param str project: Project associated with the issue, e.g. cmip6.
    :param str severity: Issue severity, e.g. low.
    :param str status: Issue status, e.g. hold.
    :param str variable: Variable associated with the issue, e.g. tos.
    :param bool subset: Flag indicating whether a subset is requested.

    :returns: List of matching issues.
    :rtype: list

    """
    if subset:
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
    else:
        qry = query(Issue)
    # qry = qry.join(IssueFacet, Issue.uid == IssueFacet.issue_uid)

    # if experiment:
    #     qry = qry.filter(IssueFacet.facet_type == 'experiment')
    #     qry = text_filter(qry, IssueFacet.facet_id, experiment)
    if institute:
        qry = text_filter(qry, Issue.institute, institute)
    # if model:
    #     qry = qry.filter(IssueFacet.facet_type == 'model')
    #     qry = text_filter(qry, IssueFacet.facet_id, model)
    if project:
        qry = text_filter(qry, Issue.project, project)
    if severity:
        qry = qry.filter(Issue.severity == severity)
    if status:
        qry = qry.filter(Issue.status == status)
    # if variable:
    #     qry = qry.filter(IssueFacet.facet_type == 'variable')
    #     qry = text_filter(qry, IssueFacet.facet_id, variable)

    return qry.all()


@validate(validate_get_issues_by_facet)
def get_issues_by_facet(facet_id, facet_type):
    """Returns issues associated with a facet.

    :param str facet_id: A facet identifier.
    :param str facet_type: Type of issue facet, e.g. dataset.

    :returns: Matching issues.
    :rtype: list

    """
    qry = raw_query(IssueFacet.issue_uid)
    qry = text_filter(qry, IssueFacet.facet_id, facet_id)
    qry = qry.filter(IssueFacet.facet_type == facet_type)

    return sorted([i[0] for i in qry.all()])
