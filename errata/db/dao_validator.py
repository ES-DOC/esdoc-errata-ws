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



def validate_delete_facets(issue_uid):
    """Function input validator: delete_facets.

    """
    v.validate_uid(issue_uid, 'Issue unique identifier')


def validate_get_facets(facet_type=None, issue_uid=None):
    """Function input validator: get_facets.

    """
    if facet_type:
        v.validate_str(facet_type, 'facet_type')
    if issue_uid:
        v.validate_uid(issue_uid, 'Issue unique identifier')


def validate_get_issue(uid):
    """Function input validator: get_issue.

    """
    v.validate_uid(uid, 'Issue unique identifier')


def validate_get_issues(criteria):
    """Function input validator: get_issues.

    """
    pass
    return

    if experiment is not None:
        v.validate_str(experiment, "Experiment name")
    if institute is not None:
        v.validate_str(institute, "Institute identifer")
    if project is not None:
        v.validate_str(project, "Project code")
    if model is not None:
        v.validate_str(model, "Model name")
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
    v.validate_str(facet_type, 'facet_type')


def validate_get_project_facets(excluded_types=[]):
    """Function input validator: get_project_facets.

    """
    v.validate_iterable(excluded_types, 'get_project_facets')

