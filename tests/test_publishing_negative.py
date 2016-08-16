# -*- coding: utf-8 -*-

"""
.. module:: test_publishing_negative.py

   :license: GPL / CeCILL
   :platform: Unix, Windows
   :synopsis: Executes web-service publishing endpoint negative tests.

.. moduleauthor:: Earth System Documentation (ES-DOC) <dev@es-doc.org>

"""
import datetime as dt
import json
import os
import uuid

import requests

from errata.utils import constants
from errata.utils import utests as tu



