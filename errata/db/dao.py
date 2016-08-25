# -*- coding: utf-8 -*-
"""
.. module:: handlers.retrieve.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - retrieve issue endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from errata.db.dao_validator import validate_delete_issue_datasets
from errata.db.dao_validator import validate_delete_issue_models
from errata.db.dao_validator import validate_get_dataset_issues
from errata.db.dao_validator import validate_get_issue
from errata.db.dao_validator import validate_get_issues
from errata.db.dao_validator import validate_get_issue_datasets
from errata.db.dao_validator import validate_get_issue_models
from errata.db.dao_validator import validate_get_model_issues
from errata.db.models import Issue
from errata.db.models import IssueDataset
from errata.db.models import IssueModel
from errata.db.session import query
from errata.db.session import raw_query
from errata.db.utils import text_filter
from errata.db.utils import as_date_string
from errata.utils.validation import validate



@validate(validate_delete_issue_datasets)
def delete_issue_datasets(uid):
    """Deletes datasets associated with an issue.

    :param str uid: Issue unique identifier.

    """
    qry = query(IssueDataset)
    qry = qry.filter(IssueDataset.issue_uid == uid)

    qry.delete()


@validate(validate_delete_issue_models)
def delete_issue_models(uid):
    """Deletes models associated with an issue.

    :param str uid: Issue unique identifier.

    """
    qry = query(IssueModel)
    qry = qry.filter(IssueModel.issue_uid == uid)

    qry.delete()


@validate(validate_get_dataset_issues)
def get_dataset_issues(dataset_id):
    """Returns issues associated with a dataset.

    :param str dataset_id: Dataset identifier.

    :returns: Matching issues.
    :rtype: list

    """
    qry = raw_query(IssueDataset.issue_uid)
    qry = text_filter(qry, IssueDataset.dataset_id, dataset_id)

    return sorted([i[0] for i in qry.all()])


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


def get_all_issues():
    """Returns all issues.

    :returns: All issues in dB.
    :rtype: list

    """
    return query(Issue).all()


@validate(validate_get_issues)
def get_issues(
    institute=None,
    project=None,
    severity=None,
    status=None
    ):
    """Returns issues that match the passed filters.

    :param str institute: Institute associated with the issue, e.g. ipsl.
    :param str project: Project associated with the issue, e.g. cmip6.
    :param str severity: Issue severity, e.g. low.
    :param str status: Issue status, e.g. hold.

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

    if institute:
        qry = qry.filter(Issue.institute == institute)
    if project:
        qry = qry.filter(Issue.project == project)
    if severity:
        qry = qry.filter(Issue.severity == severity)
    if status:
        qry = qry.filter(Issue.status == status)

    return qry.all()


@validate(validate_get_issue_datasets)
def get_issue_datasets(uid=None):
    """Returns datasets associated with an issue.

    :param str uid: Issue unique identifier.

    :returns: Matching issues.
    :rtype: list

    """
    if uid:
        qry = raw_query(IssueDataset.dataset_id)
        qry = text_filter(qry, IssueDataset.issue_uid, uid)
    else:
        qry = raw_query(
            IssueDataset.issue_uid,
            IssueDataset.dataset_id
            )

    return sorted([i[0] for i in qry.all()]) if uid else qry.all()


@validate(validate_get_issue_models)
def get_issue_models(uid=None):
    """Returns models associated with an issue.

    :param str uid: Issue unique identifier.

    :returns: Matching issues.
    :rtype: list

    """
    if uid:
        qry = raw_query(IssueModel.model_id)
        qry = text_filter(qry, IssueModel.issue_uid, uid)
    else:
        qry = raw_query(
            IssueModel.issue_uid,
            IssueModel.model_id
            )

    return sorted([i[0] for i in qry.all()]) if uid else qry.all()


@validate(validate_get_model_issues)
def get_model_issues(model_id):
    """Returns issues associated with a model.

    :param str model_id: Model identifier.

    :returns: Matching issues.
    :rtype: list

    """
    qry = raw_query(IssueModel.issue_uid)
    qry = text_filter(qry, IssueModel.model_id, model_id)

    return sorted([i[0] for i in qry.all()])
