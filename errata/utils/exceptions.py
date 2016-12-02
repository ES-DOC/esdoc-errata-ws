# -*- coding: utf-8 -*-

"""
.. module:: errata.exceptions.py
   :platform: Unix
   :synopsis: Custom exceptions used in this module for better readability of code.

.. moduleauthor:: Guillaume Levavasseur <glipsl@ipsl.jussieu.fr>


"""
from errata.utils import constants



# Processing error HTTP response code.
_HTTP_RESPONSE_SERVER_ERROR = 500

# Request validation error HTTP response code.
_HTTP_RESPONSE_INVALID_REQUEST_ERROR = 400

# Request authentication error HTTP response code.
_HTTP_UNAUTHENTICATED_ERROR = 401

# Request authorization error HTTP response code.
_HTTP_UNAUTHORIZED_ERROR = 403


class WebServiceError(Exception):
    """Web service error wrapper.

    """
    def __init__(self, msg, response_code):
        """Instance constructor.

        """
        super(WebServiceError, self).__init__(msg)
        self.response_code = response_code


class SecurityError(WebServiceError):
    """Raised if a security issue arises.

    """
    def __init__(self, msg, response_code):
        """Instance constructor.

        """
        super(SecurityError, self).__init__(
            "SECURITY EXCEPTION :: {}".format(msg)
            )
        self.response_code = response_code



class AuthenticationError(SecurityError):
    """Raised when an authentication assertion fails.

    """
    def __init__(self):
        """Instance constructor.

        """
        super(SecurityError, self).__init__(
            "AUTHENTICATION FAILED", _HTTP_UNAUTHENTICATED_ERROR
            )


class AuthorizationError(SecurityError):
    """Raised when an authorization assertion fails.

    """
    def __init__(self):
        """Instance constructor.

        """
        super(SecurityError, self).__init__(
            "AUTHORIZATION FAILED", _HTTP_UNAUTHORIZED_ERROR
            )


class RequestValidationException(WebServiceError):
    """Base class for request validation exceptions.

    """
    def __init__(self, msg):
        """Instance constructor.

        """
        super(RequestValidationException, self).__init__(
            "VALIDATION EXCEPTION :: {}".format(msg), _HTTP_RESPONSE_INVALID_REQUEST_ERROR
            )


class InvalidJSONSchemaError(RequestValidationException):
    """Raised if the submitted issue post data is invalid according to a JSON schema.

    """
    def __init__(self, json_errors):
        """Instance constructor.

        """
        super(InvalidJSONSchemaError, self).__init__(
            'ISSUE HAS INVALID JSON SCHEMA: \n{}'.format(json_errors))


class UnreachableURLError(RequestValidationException):
    """Raised if the submitted issue has unreachable (HTTP 404) urls.

    """
    def __init__(self, url):
        """Instance constructor.

        """
        super(UnreachableURLError, self).__init__(
            'URL CANNOT BE REACHED: {}'.format(url))


class InvalidIssueStatusError(RequestValidationException):
    """Raised if a submitted issue status is invalid.

    """
    def __init__(self):
        """Instance constructor.

        """
        super(InvalidIssueStatusError, self).__init__('ISSUE STATUS CHANGE NOT ALLOWED')


class ImmutableIssueAttributeError(RequestValidationException):
    """Raised if an immutable issue attribute is updated.

    """
    def __init__(self, attr_name):
        """Instance constructor.

        """
        super(ImmutableIssueAttributeError, self).__init__(
            'ISSUE ATTRIBUTE IS IMMUTABLE: {}'.format(attr_name))


class IssueDescriptionChangeRatioError(RequestValidationException):
    """Raised if an issue description changes by more than the allowed ratio.

    """
    def __init__(self, change_ratio):
        """Instance constructor.

        """
        super(IssueDescriptionChangeRatioError, self).__init__(
            "ISSUE DESCRIPTION CANNOT CHANGE BY MORE THAN {}% (Actual change ratio was {}%)".format(
                constants.DESCRIPTION_CHANGE_RATIO, 100 - change_ratio)
            )


class UnknownIssueError(RequestValidationException):
    """Raised if an issue in the process of being updated does not exist within dB.

    """
    def __init__(self, uid):
        """Instance constructor.

        """
        super(UnknownIssueError, self).__init__(
            "ISSUE IS UNKNOWN: {}".format(uid)
            )
