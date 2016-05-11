# -*- coding: utf-8 -*-

"""
.. module:: db.dao_validator.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - db data access validator.


.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from errata import constants
from errata.utils import validation as v



def validate_get_issue(uid):
    """Function input validator: get_issue.

    """
    v.validate_uid(uid, 'Issue unique identifier')


def validate_get_issues(
    project=None,
    severity=None,
    state=None,
    workflow=None
    ):
    """Function input validator: get_issues.

    """
    if project is not None:
        v.validate_str(project, "Project code")

    if severity is not None:
        v.validate_str(severity, "Issue severity")
        v.validate_enum(
            [i['key'] for i in constants.SEVERITY], severity, "Issue severity")

    if state is not None:
        v.validate_str(state, "Issue state")
        v.validate_enum(
            [i['key'] for i in constants.STATUS], state, "Issue state")

    if workflow is not None:
        v.validate_str(workflow, "Issue workflow")
        v.validate_enum(
            [i['key'] for i in constants.WORKFLOW], workflow, "Issue workflow")
