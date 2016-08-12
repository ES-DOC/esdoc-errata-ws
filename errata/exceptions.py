# -*- coding: utf-8 -*-

"""
.. module:: errata.exceptions.py
   :platform: Unix
   :synopsis: Custom exceptions used in this module for better readability of code.

.. moduleauthor:: Guillaume Levavasseur <glipsl@ipsl.jussieu.fr>


"""
from errata import constants



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


class DuplicateDescriptionError(Exception):
    """Raised if a submitted issue description already exists.

    """
    def __init__(self):
        """Instance constructor.

        """
        super(DuplicateDescriptionError, self).__init__('ISSUE DESCRIPTION ALREADY EXISTS')


class InvalidStatusError(Exception):
    """Raised if a submitted issue status is invalid.

    """
    def __init__(self):
        """Instance constructor.

        """
        super(InvalidStatusError, self).__init__('ISSUE STATUS CHANGE NOT ALLOWED')


class ImmutableAttributeError(Exception):
    """Raised if an immutable issue attribute is updated.

    """
    def __init__(self):
        """Instance constructor.

        """
        super(ImmutableAttributeError, self).__init__('ISSUE ATTRIBUTE IS IMMUTABLE')


class InvalidDescriptionChangeRatioError(Exception):
    """Raised if an issue description changes by more than the allowed ratio.

    """
    def __init__(self):
        """Instance constructor.

        """
        super(InvalidDescriptionChangeRatioError, self).__init__(
            "ISSUE DESCRIPTION CANNOT CHANGE BY MORE THAN {}%".format(constants.RATIO)
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
