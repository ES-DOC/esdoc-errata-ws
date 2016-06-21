"""
Custom exceptions used in this module for better readability of code.

Author: Atef BEN NASSER (IPSL), 2016
"""


class UnresolvedAggregationLevel(Exception):
    """
    To be raised if the aggregation level found is neither DATASET or FILE.
    """
    def __init__(self, **args):

        # Default message
        self.msg = 'UNRESOLVABLE AGGREGATION LEVEL RECEIVED FROM HANDLE SERVER'
        super(self.__class__, self).__init__(self.msg)

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
    To be raised if a file is no longer traceable for whatever reason.
    """
    def __init__(self, **args):

        # Default message:
        self.msg = 'FILE WAS NOT FOUND IN SUCCESSOR'
        super(self.__class__, self).__init__(self.msg)
