# -*- coding: utf-8 -*-
"""

.. module:: constants_json.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - web-service JSON content related constants.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from errata.utils.constants import *



# JSON field names.
JF_DATE_CLOSED = 'dateClosed'
JF_DATE_CREATED = 'dateCreated'
JF_DATE_UPDATED = 'dateUpdated'
JF_DESCRIPTION = 'description'
JF_DATASETS = 'datasets'
JF_EXPERIMENT = 'experiment'
JF_INSTITUTE = 'institute'
JF_MATERIALS = 'materials'
JF_MODEL = 'model'
JF_PROJECT = 'project'
JF_SEVERITY = 'severity'
JF_STATUS = 'status'
JF_TITLE = 'title'
JF_UID = 'uid'
JF_URL = 'url'
JF_VARIABLE = 'variable'


# Map of facet types to corresponding JSON fields.
FACET_TYPE_JSON_FIELD = {
	FACET_TYPE_DATASET: JF_DATASETS,
	FACET_TYPE_EXPERIMENT: JF_EXPERIMENT,
	FACET_TYPE_INSTITUTE: JF_INSTITUTE,
	FACET_TYPE_MODEL: JF_MODEL,
	FACET_TYPE_PROJECT: JF_PROJECT,
	FACET_TYPE_SEVERITY: JF_SEVERITY,
	FACET_TYPE_STATUS: JF_STATUS,
	FACET_TYPE_VARIABLE: JF_VARIABLE
}
