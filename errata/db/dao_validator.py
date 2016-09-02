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
        print "TODO: validate facet type in supported set"


def validate_get_facets(issue_uid=None):
    """Function input validator: get_facets.

    """
    if issue_uid:
        v.validate_uid(issue_uid, 'Issue unique identifier')


def validate_get_issue(uid):
    """Function input validator: get_issue.

    """
    v.validate_uid(uid, 'Issue unique identifier')


def validate_get_issues(
    institute=None,
    project=None,
    severity=None,
    status=None,
    subset=False
    ):
    """Function input validator: get_issues.

    """
    if institute is not None:
        v.validate_str(institute, "Institute code")

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

    v.validate_bool(subset, "Issue subset")


def validate_get_issues_by_facet(facet_id, facet_type):
    """Function input validator: get_issues_by_facet.

    """
    v.validate_str(facet_id, "Facet identifier")
    print "TODO: validate facet type in supported set"
