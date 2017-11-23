# -*- coding: utf-8 -*-
"""
.. module:: utils.misc.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Miscellaneous utility functions.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
def traverse(target, tree_types=(list, tuple)):
    """Iterates through a list of lists and extracts items.

    :param object target: Target to be traversed.
    :param tuple tree_types: Iterable types

    :returns: An iterable list of extracted items.
    :rtype: generator

    """
    if isinstance(target, tree_types):
        for item in target:
            for child in traverse(item, tree_types):
                yield child
    else:
        yield target
