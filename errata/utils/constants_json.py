# -*- coding: utf-8 -*-
"""

.. module:: constants_json.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - web-service JSON content related constants.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from errata.utils.constants import FACET_TYPE_DATASET
from errata.utils.constants import FACET_TYPE_INSTITUTE
from errata.utils.constants import FACET_TYPE_PROJECT
from errata.utils.constants import FACET_TYPE_SEVERITY
from errata.utils.constants import FACET_TYPE_STATUS



# JSON field names.
JF_DATE_CLOSED = 'dateClosed'
JF_DATE_CREATED = 'dateCreated'
JF_DATE_UPDATED = 'dateUpdated'
JF_DESCRIPTION = 'description'
JF_DATASETS = 'datasets'
JF_FACETS = 'facets'
JF_INSTITUTE = 'institute'
JF_MATERIALS = 'materials'
JF_PROJECT = 'project'
JF_SEVERITY = 'severity'
JF_STATUS = 'status'
JF_TITLE = 'title'
JF_UID = 'uid'
JF_URL = 'url'

# Map of json fields to facets for extraction.
JF_FACET_TYPE_MAP = {
    JF_DATASETS: FACET_TYPE_DATASET,
    JF_INSTITUTE: FACET_TYPE_INSTITUTE,
    JF_PROJECT: FACET_TYPE_PROJECT,
    JF_SEVERITY: FACET_TYPE_SEVERITY,
    JF_STATUS: FACET_TYPE_STATUS
}
