# -*- coding: utf-8 -*-
"""
.. module:: db.dao.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - db data access.

.. moduleauthor:: Atef Ben nasser <abenasser@ipsl.jussieu.fr>


"""
from errata.db.models import Issue
from errata.db.session import query
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


def get_issues(state=None, workflow=None):
    """Returns an issue.

    :param str state: Issue state, e.g. open.
    :param str status: Issue workflow, e.g. hold.

    :returns: List of matching issues.
    :rtype: list

    """
    qry = query(Issue)
    if state:
        qry = text_filter(qry, Issue.state, state)
    if workflow:
        qry = text_filter(qry, Issue.workflow, workflow)

    return qry.all()


def get_issues_by_uids(uid_list):
    """Returns list of issues relative to a list of uids.

    :param list uids: List of issue uids.

    :return: list of issues
    :rtype: list of db.models.Issue

    """
    return [get_issue(uid) for uid in uid_list]
