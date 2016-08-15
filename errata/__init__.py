# -*- coding: utf-8 -*-
#                             __
#   _______________________ _/  |______            __  _  ________
# _/ __ \_  __ \_  __ \__  \\   __\__  \    ______ \ \/ \/ /  ___/
# \  ___/|  | \/|  | \// __ \|  |  / __ \_ /_____/  \     /\___ \
#  \___  >__|   |__|  (____  /__| (____  /           \/\_//____  >
#      \/                  \/          \/                      \/
#
"""
.. module:: errata.__init__.py

   :license: GPL / CeCILL
   :platform: Unix, Windows
   :synopsis: Package initializer.

.. moduleauthor:: Earth System Documentation (ES-DOC) <dev@es-doc.org>

"""
__title__ = 'errata web service'
__version__ = '0.2.0.0.0'
__author__ = 'ES-DOC'
__license__ = 'GPL'
__copyright__ = 'Copyright 2016: IPSL'

from errata.app import run
from errata.app import stop
