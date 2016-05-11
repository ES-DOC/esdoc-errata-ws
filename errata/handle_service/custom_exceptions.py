"""
Custom exceptions used in this module for better readability of code.

Author: Atef BEN NASSER (IPSL), 2016
"""


class HandleNotFoundException(Exception):
    """
    To be raised if the self.handle was not found on the Handle Server.
    """
    def __init__(self, **args):

        # Default message:
        self.msg = 'HANDLE WAS NOT FOUND ON HANDLE SERVER'
        super(self.__class__, self).__init__(self.msg)


class FileNotFoundInSuccessor(Exception):
    """
    To be raised if a file disappears from tree.
    """
    def __init__(self, **args):

        # Default message:
        self.msg = 'FILE WAS NOT FOUND IN SUCCESSOR'
        super(self.__class__, self).__init__(self.msg)
