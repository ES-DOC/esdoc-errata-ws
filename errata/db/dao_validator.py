# -*- coding: utf-8 -*-

"""
.. module:: db.dao_validator.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - db data access validator.


.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from errata.utils import constants
from errata.utils import validation as v



def validate_delete_facets(issue_uid, facet_type=None):
    """Function input validator: delete_facets.

    """
    v.validate_uid(issue_uid, 'Issue unique identifier')
    if facet_type:
        v.validate_enum(constants.FACET_TYPE, facet_type, "facet_type")


def validate_get_facets(facet_type=None):
    """Function input validator: get_facets.

    """
    if facet_type:
        v.validate_enum(constants.FACET_TYPE, facet_type, "facet_type")


def validate_get_issue(uid):
    """Function input validator: get_issue.

    """
    v.validate_uid(uid, 'Issue unique identifier')


def validate_get_issue_facets(uid, facet_type=None):
    """Function input validator: get_issue.

    """
    v.validate_uid(uid, 'Issue unique identifier')
    if facet_type:
        v.validate_enum(constants.FACET_TYPE, facet_type, "facet_type")


def validate_get_issues(
    experiment=None,
    institute=None,
    model=None,
    project=None,
    severity=None,
    status=None,
    variable=None
    ):
    """Function input validator: get_issues.

    """
    if experiment is not None:
        v.validate_str(experiment, "Experiment name")
    if institute is not None:
        v.validate_str(institute, "Institute code")
    if model is not None:
        v.validate_str(model, "Model name")
    if project is not None:
        v.validate_str(project, "Project code")
    if severity is not None:
        v.validate_str(severity, "Issue severity")
        v.validate_enum(
            [i['key'] for i in constants.SEVERITY], severity, "Issue severity")
    if status is not None:
        v.validate_str(status, "Issue status")
        v.validate_enum(
            [i['key'] for i in constants.STATUS], status, "Issue status")
    if variable is not None:
        v.validate_str(variable, "Variable name")


def validate_get_issues_by_facet(facet_value, facet_type):
    """Function input validator: get_issues_by_facet.

    """
    v.validate_str(facet_value, "Facet value")
    v.validate_enum(constants.FACET_TYPE, facet_type, "facet_type")
