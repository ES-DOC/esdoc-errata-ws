# -*- coding: utf-8 -*-
"""

.. module:: constants.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - web-service constants.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import datetime as dt
import random
import uuid



# HTTP CORS header.
HTTP_HEADER_Access_Control_Allow_Origin = "Access-Control-Allow-Origin"

# Default endpoint.
DEFAULT_ENDPOINT = r'/1/ops/heartbeat'

# Search facet type - dataset.
FACET_TYPE_DATASET = 'dataset'

# Search facet type - model.
FACET_TYPE_EXPERIMENT = 'experiment'

# Search facet type - model.
FACET_TYPE_MODEL = 'model'

# Search facet type - variable.
FACET_TYPE_VARIABLE = 'variable'

# Search facet type set.
FACET_TYPE = {
	FACET_TYPE_DATASET,
	FACET_TYPE_EXPERIMENT,
	FACET_TYPE_MODEL,
	FACET_TYPE_VARIABLE
}

# Issue status - new.
STATUS_NEW = u'new'

# Issue status - on hold.
STATUS_ON_HOLD = u'onhold'

# Issue status - resolved.
STATUS_RESOLVED = u'resolved'

# Issue status - won fix.
STATUS_WONT_FIX = u'wontfix'

# Issue status set.
STATUS = [
	{
		'color': "#00ff00",
		'label': 'New',
		'key': STATUS_NEW
	},
	{
		'color': "#ff9900",
		'label': 'On Hold',
		'key': STATUS_ON_HOLD
	},
	{
		'color': "#0c343d",
		'label': 'Resolved',
		'key': STATUS_RESOLVED
	},
	{
		'color': "#38761d",
		'label': 'Wont Fix',
		'key': STATUS_WONT_FIX
	},
]

# Issue severity - low.
SEVERITY_LOW = u"low"

# Issue severity - medium.
SEVERITY_MEDIUM = u"medium"

# Issue severity - high.
SEVERITY_HIGH = u"high"

# Issue severity - critical.
SEVERITY_CRITICAL = u"critical"

# Issue severity level set.
SEVERITY = [
	{
		'color': "#e6b8af",
		'label': 'Low',
		'key': SEVERITY_LOW,
		'sortOrdinal': 0
	},
	{
		'color': "#dd7e6b",
		'label': 'Medium',
		'key': SEVERITY_MEDIUM,
		'sortOrdinal': 1
	},
	{
		'color': "#cc4125",
		'label': 'High',
		'key': SEVERITY_HIGH,
		'sortOrdinal': 2
	},
	{
		'color': "#a61c00",
		'label': 'Critical',
		'key': SEVERITY_CRITICAL,
		'sortOrdinal': 3
	},
]

# TODO - leverage pyessv
# Project - cmip5.
PROJECT_CMIP5 = u"cmip5"

# Project - cmip6.
PROJECT_CMIP6 = u"cmip6"

# Project - test.
PROJECT_TEST = u"test"

# Project - all.
PROJECT = [
	{
	    'key': PROJECT_CMIP5,
	    'label': u"CMIP5"
	},
	{
	    'key': PROJECT_CMIP6,
	    'label': u"CMIP6"
	},
	{
	    'key': PROJECT_TEST,
	    'label': u"TEST"
	}
]


# TODO - leverage pyessv
# Institute - BADC.
INSTITUTE_BADC = u"badc"

# Institute - DKRZ.
INSTITUTE_DKRZ = u"dkrz"

# Institute - IPSL.
INSTITUTE_IPSL = u"ipsl"

# Institute - all.
INSTITUTE = [
	{
	    'key': INSTITUTE_BADC,
	    'label': u"BADC"
	},
	{
	    'key': INSTITUTE_DKRZ,
	    'label': u"DKRZ"
	},
	{
	    'key': INSTITUTE_IPSL,
	    'label': u"IPSL"
	}
]

# List of issue attributes that cannot be updated.
IMMUTABLE_ISSUE_ATTRIBUTES = [
	'title',
	'project',
	'institute',
	# 'dateCreated'
	]

# Ratio of similarity between descriptions of updated and database issue.
DESCRIPTION_CHANGE_RATIO = 20

# Test issue.
ISSUE = {
    'datasets': [
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.1pctCO2.yr.ocnBgchem.Oyr.r1i1p1#20161010",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r10i1p1#20110922",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r11i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r12i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r1i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r1i1p1#20130322",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r2i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r3i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r4i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r6i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r7i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r8i1p1#20110901",
        u"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r9i1p1#20110901"
        ],
    'dateCreated': unicode(dt.datetime.utcnow()),
    'description': unicode(uuid.uuid4()),
    'experiments': [
    	u"1pctCO2",
    	u"abrupt4xCO2"
    ],
    'institute': random.choice(INSTITUTE)['key'],
    'materials': [
        u"http://errata.ipsl.upmc.fr/static/images_errata/time.jpg",
        u"http://errata.ipsl.upmc.fr/static/images_errata/time5.jpg"
    ],
    'models': [
        u"IPSL-CM5A-LR"
    ],
    'project': random.choice(PROJECT)['key'],
    'severity': random.choice(SEVERITY)['key'],
    'status': STATUS_NEW,
    'title': unicode(uuid.uuid4()),
    'uid': unicode(uuid.uuid4()),
    'url': u"http://errata.ipsl.upmc.fr/issue/1",
    'variables': [
    	u"bsi",
    	u"dcalc",
    	u"pp"
    ]
    }

ORGS_IDS = [23123271]
