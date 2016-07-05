# -*- coding: utf-8 -*-

"""
.. module:: errata.issue_manager.custom_exceptions.py
   :platform: Unix
   :synopsis: Custom exceptions used in this module for better readability of code.

.. moduleauthor:: Guillaume Levavasseur <glipsl@ipsl.jussieu.fr>


"""


class InvalidJSONSchema(Exception):
    """
    To be raised if the submitted self.issue has invalid JSON schema.
    """
    def __init__(self, **args):

        # Default message:
        self.msg = 'ISSUE HAS INVALID JSON SCHEMA'
        super(self.__class__, self).__init__(self.msg)


class UnreachableURLs(Exception):
    """
    To be raised if the submitted self.issue.url or self.issue.materials have unreachable URLs.
    """
    def __init__(self, **args):

        # Default message:
        self.msg = 'URLS CANNOT BE REACHED'
        super(self.__class__, self).__init__(self.msg)


class InvalidDatasetIDs(Exception):
    """
    To be raised if the submitted self.dsets has invalid dataset ID pattern.
    """
    def __init__(self, **args):

        # Default message:
        self.msg = 'INVALID DATASET ID PATTERN'
        super(self.__class__, self).__init__(self.msg)


class InvalidDescription(Exception):
    """
    To be raised if the submitted self.issue.description already exists.
    """
    def __init__(self, **args):

        # Default message:
        self.msg = 'DESCRIPTION ALREADY EXISTS'
        super(self.__class__, self).__init__(self.msg)


class InvalidStatus(Exception):
    """
    To be raised if the submitted self.issue.status is not allowed.
    """
    def __init__(self, **args):

        # Default message:
        self.msg = 'STATUS CHANGE NOT ALLOWED'
        super(self.__class__, self).__init__(self.msg)


class InvalidAttribute(Exception):
    """
    To be raised if the submitted self.issue.status is not allowed.
    """

    def __init__(self, **args):
        # Default message:
        self.msg = 'ATTRIBUTE SHOULD BE UNCHANGED'
        super(self.__class__, self).__init__(self.msg)


class InvalidDescription(Exception):
    """
    To be raised if the submitted self.issue.status is not allowed.
    """

    def __init__(self, **args):
        # Default message:
        self.msg = 'DESCRIPTION CHANGE BY MORE THAN 80%'
        super(self.__class__, self).__init__(self.msg)
