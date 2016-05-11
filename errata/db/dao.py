# -*- coding: utf-8 -*-
"""
.. module:: db.dao.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - db data access.

.. moduleauthor:: Atef Ben nasser <abenasser@ipsl.jussieu.fr>


"""
from errata.db.dao_validator import validate_get_issue
from errata.db.dao_validator import validate_get_issues
from errata.db.models import Issue
from errata.db.session import query
from errata.db.utils import text_filter
from errata.utils.validation import validate



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
    project=None,
    severity=None,
    state=None,
    workflow=None
    ):
    """Returns an issue.

    :param str project: Project associated with the issue state, e.g. cmip6.
    :param str severity: Issue severity, e.g. low.
    :param str state: Issue state, e.g. open.
    :param str status: Issue workflow, e.g. hold.

    :returns: List of matching issues.
    :rtype: list

    """
    qry = query(Issue)
    if project:
        qry = qry.filter(Issue.project == project)
    if severity:
        qry = qry.filter(Issue.severity == severity)
    if state:
        qry = qry.filter(Issue.state == state)
    if workflow:
        qry = qry.filter(Issue.workflow == workflow)

    return qry.all()
