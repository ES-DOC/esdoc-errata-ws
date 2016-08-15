# -*- coding: utf-8 -*-

"""
.. module:: errata.exceptions.py
   :platform: Unix
   :synopsis: Custom exceptions used in this module for better readability of code.

.. moduleauthor:: Guillaume Levavasseur <glipsl@ipsl.jussieu.fr>


"""
from errata.utils import constants



class InvalidJSONSchemaError(Exception):
    """Raised if the submitted issue post data is invalid according to a JSON schema.

    """
    def __init__(self, json_errors):
        """Instance constructor.

        """
        super(InvalidJSONSchemaError, self).__init__(
            'ISSUE HAS INVALID JSON SCHEMA: \n{}'.format(json_errors))


class UnreachableURLError(Exception):
    """Raised if the submitted issue has unreachable (HTTP 404) urls.

    """
    def __init__(self, url):
        """Instance constructor.

        """
        super(UnreachableURLError, self).__init__(
            'URL CANNOT BE REACHED: {}'.format(url))


class InvalidDatasetIdentiferError(Exception):
    """Raised if a submitted dataset identifier is invalid.

    """
    def __init__(self, dataset_id):
        """Instance constructor.

        """
        super(InvalidDatasetIdentiferError, self).__init__(
            'INVALID DATASET ID: {}'.format(dataset_id))


class DuplicateIssueDescriptionError(Exception):
    """Raised if a submitted issue description already exists.

    """
    def __init__(self):
        """Instance constructor.

        """
        super(DuplicateIssueDescriptionError, self).__init__('ISSUE DESCRIPTION ALREADY EXISTS')


class InvalidIssueStatusError(Exception):
    """Raised if a submitted issue status is invalid.

    """
    def __init__(self):
        """Instance constructor.

        """
        super(InvalidIssueStatusError, self).__init__('ISSUE STATUS CHANGE NOT ALLOWED')


class ImmutableIssueAttributeError(Exception):
    """Raised if an immutable issue attribute is updated.

    """
    def __init__(self, attr_name):
        """Instance constructor.

        """
        super(ImmutableIssueAttributeError, self).__init__(
            'ISSUE ATTRIBUTE IS IMMUTABLE: {}'.format(attr_name))


class IssueDescriptionChangeRatioError(Exception):
    """Raised if an issue description changes by more than the allowed ratio.

    """
    def __init__(self, change_ratio):
        """Instance constructor.

        """
        super(IssueDescriptionChangeRatioError, self).__init__(
            "ISSUE DESCRIPTION CANNOT CHANGE BY MORE THAN {}% (Actual change ratio was {}%)".format(
                constants.DESCRIPTION_CHANGE_RATIO, 100 - change_ratio)
            )


class UnknownIssueError(Exception):
    """Raised if an issue in the process of being updated does not exist within dB.

    """
    def __init__(self, uid):
        """Instance constructor.

        """
        super(UnknownIssueError, self).__init__(
            "ISSUE IS UNKNOWN: {}".format(uid)
            )


class SecurityError(Exception):
    """Raised if a security issue arises.

    """
    def __init__(self, msg):
        """Instance constructor.

        """
        super(SecurityError, self).__init__(
            "SECURITY EXCEPTION :: {}".format(msg)
            )