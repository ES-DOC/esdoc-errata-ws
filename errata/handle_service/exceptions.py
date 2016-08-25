# -*- coding: utf-8 -*-
"""
.. module:: handle_service.exceptions.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Handle service custom exceptions.

.. moduleauthor:: Atef Bennasser <abennasser@ipsl.jussieu.fr>


"""
class UnresolvedAggregationLevel(Exception):
    """Raised if aggregation level found is neither DATASET or FILE.

    """
    def __init__(self, **args):
        """Instance constructor.

        """
        super(UnresolvedAggregationLevel, self).__init__(
            'UNRESOLVABLE AGGREGATION LEVEL RECEIVED FROM HANDLE SERVER'
            )


class HandleNotFoundError(Exception):
    """Raised if handle was not found on the Handle Server.

    """
    def __init__(self, **args):
        """Instance constructor.

        """
        super(HandleNotFoundError, self).__init__(
            'HANDLE WAS NOT FOUND ON HANDLE SERVER'
            )


class FileNotFoundInHandle(Exception):
    """Raised if file is no longer traceable for whatever reason.

    """
    def __init__(self, **args):
        """Instance constructor.

        """
        self.message = 'File missing from previous dataset, this maybe due to filename change, errata information ' \
                       'cannot be deduced any further'
        super(FileNotFoundInHandle, self).__init__(
            'FILE WAS NOT FOUND IN DATASET'
            )
