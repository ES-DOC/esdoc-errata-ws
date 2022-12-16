import pyessv

from errata_ws.utils import constants
from errata_ws.utils import validation as v



def validate_delete_facets(issue_uid):
    """Function input validator: delete_facets.

    """
    v.validate_uid(issue_uid, 'Issue unique identifier')


def validate_delete_resources(issue_uid):
    """Function input validator: delete_resources.

    """
    v.validate_uid(issue_uid, 'Issue unique identifier')


def validate_get_datasets(issue_uid):
    """Function input validator: get_datasets.

    """
    v.validate_uid(issue_uid, 'Issue unique identifier')


def validate_get_issue(uid):
    """Function input validator: get_issue.

    """
    v.validate_uid(uid, 'Issue unique identifier')


def validate_get_issues(criteria=None):
    """Function input validator: get_issues.

    """
    if criteria is None:
        return

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
        v.validate_pyessv_enum('esdoc:errata:severity', severity, "Issue severity")
    if status is not None:
        v.validate_str(status, "Issue status")
        v.validate_pyessv_enum('esdoc:errata:status', status, "Issue status")
    if variable is not None:
        v.validate_str(variable, "Variable name")


def validate_get_resources(issue_uid=None):
    """Function input validator: get_resources.

    """
    if issue_uid is not None:
        v.validate_uid(issue_uid, 'Issue unique identifier')
