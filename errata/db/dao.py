# -*- coding: utf-8 -*-
"""
.. module:: handlers.retrieve.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - retrieve issue endpoint.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from errata.db.dao_validator import validate_get_issue
from errata.db.dao_validator import validate_get_issues
from errata.db.dao_validator import validate_get_issue_datasets
from errata.db.dao_validator import validate_get_issue_datasets_by_uid

from errata.db.models import Issue
from errata.db.models import IssueDataset
from errata.db.session import query
from errata.db.session import raw_query
from errata.db.utils import text_filter
from errata.db.utils import as_date_string
from errata.utils.validation import validate


@validate(validate_get_issue)
def get_issue(uid):
    """Returns an issue.

    :param str uid: Issue unique identifier.

    :returns: First matching issue.
    :rtype: db.models.Issue

    """
    print('querying issue...')
    qry = query(Issue)
    qry = text_filter(qry, Issue.uid, uid)

    return qry.first()


@validate(validate_get_issue_datasets)
def get_issue_datasets(issue_id):
    """Returns datasets associated with an issue.

    :param int issue_id: Issue identifier.

    :returns: Matching issues.
    :rtype: list

    """

    qry = raw_query(IssueDataset.dataset_id)
    qry = qry.filter(IssueDataset.issue_id == issue_id)
    qry = qry.order_by(IssueDataset.dataset_id)

    return qry.all()


@validate(validate_get_issue_datasets_by_uid)
def get_issue_datasets_by_uid(issue_uid):
    """Returns datasets associated with an issue.

    :param string issue_uid: Issue uid.

    :returns: Matching issues.
    :rtype: list

    """
    print('YOLO ' + issue_uid)
    issues = raw_query(Issue)
    print('Got all issues with the provided uid')
    issues = issues.filter(Issue.uid == issue_uid)
    # issues = issues.first()
    # real_issue = real_issue.first()
    # print(real_issue.all())
    print(type(issues))
    print(issues)
    print(issues is None)
    try:
        print(issues.first().id)
    except Exception as e:
        print(repr(e))
    print('HERE')
    qry = raw_query(IssueDataset)
    qry = qry.filter(IssueDataset.issue_id == issues.first().id)
    qry = qry.order_by(IssueDataset.dataset_id)
    print(qry.all())
    print("DONE!")
    return qry.all()


# @validate()
def get_dset_by_id(dset_id):
    pass


@validate(validate_get_issues)
def get_issues(
    institute=None,
    project=None,
    severity=None,
    state=None,
    workflow=None
    ):
    """Returns an issue.

    :param str institute: Institute associated with the issue, e.g. ipsl.
    :param str project: Project associated with the issue, e.g. cmip6.
    :param str severity: Issue severity, e.g. low.
    :param str state: Issue state, e.g. open.
    :param str status: Issue workflow, e.g. hold.

    :returns: List of matching issues.
    :rtype: list

    """
    qry = raw_query(
        Issue.project,
        Issue.institute,
        Issue.uid,
        Issue.title,
        Issue.state,
        Issue.severity,
        Issue.workflow,
        as_date_string(Issue.date_created),
        as_date_string(Issue.date_updated)
        )

    if institute:
        qry = qry.filter(Issue.institute == institute)
    if project:
        qry = qry.filter(Issue.project == project)
    if severity:
        qry = qry.filter(Issue.severity == severity)
    if state:
        qry = qry.filter(Issue.state == state)
    if workflow:
        qry = qry.filter(Issue.workflow == workflow)

    return qry.all()


def check_description(description):
    """
    Checks for the existence of a similar description in the db.
    :param description: string
    :return: boolean
    """

    qry = raw_query(Issue.description)
    qry = qry.filter(Issue.description == description)
    if not qry.all():
        return True
    else:
        return False

