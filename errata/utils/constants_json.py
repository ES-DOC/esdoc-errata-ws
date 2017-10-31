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
JF_DATE_CLOSED = u'dateClosed'
JF_DATE_CREATED = u'dateCreated'
JF_DATE_UPDATED = u'dateUpdated'
JF_DESCRIPTION = u'description'
JF_DATASETS = u'datasets'
JF_FACETS = u'facets'
JF_INSTITUTE = u'institute'
JF_MATERIALS = u'materials'
JF_PROJECT = u'project'
JF_SEVERITY = u'severity'
JF_STATUS = u'status'
JF_TITLE = u'title'
JF_UID = u'uid'
JF_URL = u'url'

# Map of json fields to facets for extraction.
JF_FACET_TYPE_MAP = {
    JF_DATASETS: FACET_TYPE_DATASET,
    JF_INSTITUTE: FACET_TYPE_INSTITUTE,
    JF_PROJECT: FACET_TYPE_PROJECT,
    JF_SEVERITY: FACET_TYPE_SEVERITY,
    JF_STATUS: FACET_TYPE_STATUS
}
