# -*- coding: utf-8 -*-

"""
.. module:: utils.exceptions.py
   :platform: Unix
   :synopsis: Custom exceptions used in this module for better readability of code.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import pyesdoc

from errata.utils import constants



class WebServiceError(Exception):
    """Web service error wrapper.

    """
    def __init__(self, msg, response_code):
        """Instance constructor.

        """
        super(WebServiceError, self).__init__(msg)
        self.response_code = response_code


class RequestValidationException(WebServiceError):
    """Base class for request validation exceptions.

    """
    def __init__(self, msg):
        """Instance constructor.

        """
        super(RequestValidationException, self).__init__(msg, constants.HTTP_RESPONSE_BAD_REQUEST_ERROR)


class InvalidJSONError(RequestValidationException):
    """Raised if the submitted issue post data is invalid according to a JSON schema.

    """
    def __init__(self, json_err):
        """Instance constructor.

        """
        msg = json_err.message.strip()
        try:
            self.field = json_err.path[0]
        except Exception as err:
            self.field = msg.split("'")[1]
        super(InvalidJSONError, self).__init__(msg)


class InvalidDatasetIdentifierError(RequestValidationException):
    """Raised if the submitted issue post data contains an invalid dataset identifer.

    """
    def __init__(self):
        """Instance constructor.

        """
        self.field = constants.JF_DATASETS
        msg = 'ISSUE HAS INVALID DATASET IDENTIFIER'
        super(InvalidDatasetIdentifierError, self).__init__(msg)


class MultipleInstitutesError(RequestValidationException):
    """Raised if the submitted issue post data contains an multiple institute identifers.

    """
    def __init__(self):
        """Instance constructor.

        """
        self.field = constants.JF_DATASETS
        msg = 'ISSUE HAS MULTIPLE INSTITUTES'
        super(MultipleInstitutesError, self).__init__(msg)


class InvalidURLError(RequestValidationException):
    """Raised if the submitted issue has unreachable (HTTP 404) urls.

    """
    def __init__(self, url):
        """Instance constructor.

        """
        self.field = constants.JF_URLS
        msg = 'URL INVALID: {}'.format(url)
        super(InvalidURLError, self).__init__(msg)


class IssueStatusChangeError(RequestValidationException):
    """Raised if a submitted issue status is invalid.

    """
    def __init__(self):
        """Instance constructor.

        """
        self.field = constants.JF_STATUS
        msg = 'ISSUE STATUS CHANGE NOT ALLOWED'
        super(IssueStatusChangeError, self).__init__(msg)


class IssueImmutableAttributeError(RequestValidationException):
    """Raised if an immutable issue attribute is updated.

    """
    def __init__(self, attr_name):
        """Instance constructor.

        """
        self.field = attr_name
        msg = 'ISSUE ATTRIBUTE IS IMMUTABLE: {}'.format(attr_name)
        super(IssueImmutableAttributeError, self).__init__(msg)


class UnknownIssueError(RequestValidationException):
    """Raised if an issue in the process of being updated does not exist within dB.

    """
    def __init__(self, uid):
        """Instance constructor.

        """
        self.field = constants.JF_UID
        msg = "ISSUE IS UNKNOWN: {}".format(uid)
        super(UnknownIssueError, self).__init__(msg)


# Map of managed error codes.
ERROR_CODES = {
    InvalidJSONError: 900,
    InvalidDatasetIdentifierError: 901,
    MultipleInstitutesError: 902,
    InvalidURLError: 903,
    UnknownIssueError: 904,
    IssueStatusChangeError: 905,
    IssueImmutableAttributeError: 906,
    pyesdoc.AuthenticationError: 990,
    pyesdoc.AuthorizationError: 991
}
