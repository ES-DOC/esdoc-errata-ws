# -*- coding: utf-8 -*-
"""
.. module:: db.dao.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - db data access.

.. moduleauthor:: Atef Ben nasser <abenasser@ipsl.jussieu.fr>


"""
from errata.db.session import query
from errata.db.models import Issue
from errata.db.utils import text_filter


def get_issue(uid):
    """Returns an issue.

    :param str uid: Issue unique identifier.

    :returns: First matching issue.
    :rtype: db.models.Issue

    """
    qry = query(Issue)
    qry = text_filter(qry, Issue.uid, uid)

    return qry.first()


def get_issues(status=None):
    """Returns an issue.

    :param str status: Issue status filter field.

    :returns: First matching issue.
    :rtype: db.models.Issue

    """
    qry = query(Issue)
    if status:
        qry = text_filter(qry, Issue.status, status)

    return qry.all()


def get_issues_by_uids(list_of_uids):
    """
    returns list of issues relative to a list of uids
    :param list_of_uids: list of uids
    :return: list of issues
    :rtype: list of db.models.Issue
    """
    qry = query(Issue)
    list_of_issues = []
    for uid in list_of_uids:
        list_of_issues.append(get_issue(uid))
    return list_of_issues


def get_issue(state):
    """Returns issues corresponding to a state.

    :param str state: State of the issue (new, on hold, wont fix, closed).

    :returns: First matching issue.
    :rtype: db.models.Issue

    """
    qry = query(Issue)
    qry = text_filter(qry, Issue.state, state)

    return qry.all()
