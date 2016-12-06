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

from errata.utils.constants import INSTITUTE
from errata.utils.constants import PROJECT
from errata.utils.constants import SEVERITY
from errata.utils.constants import STATUS_NEW
from errata.utils.constants_json import JF_DATASETS
from errata.utils.constants_json import JF_DATE_CREATED
from errata.utils.constants_json import JF_DESCRIPTION
from errata.utils.constants_json import JF_EXPERIMENTS
from errata.utils.constants_json import JF_INSTITUTE
from errata.utils.constants_json import JF_MATERIALS
from errata.utils.constants_json import JF_MODELS
from errata.utils.constants_json import JF_PROJECT
from errata.utils.constants_json import JF_SEVERITY
from errata.utils.constants_json import JF_STATUS
from errata.utils.constants_json import JF_TITLE
from errata.utils.constants_json import JF_UID
from errata.utils.constants_json import JF_URL
from errata.utils.constants_json import JF_VARIABLES



# Test issue datasets.
ISSUE_DATASETS = [
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
]

# Test issue experiments.
ISSUE_EXPERIMENTS = [
	u"1pctCO2",
	u"abrupt4xCO2"
]

# Test issue materials.
ISSUE_MATERIALS = [
    u"http://errata.ipsl.upmc.fr/static/images_errata/time.jpg",
    u"http://errata.ipsl.upmc.fr/static/images_errata/time2.jpg",
    u"http://errata.ipsl.upmc.fr/static/images_errata/time3.jpg",
    u"http://errata.ipsl.upmc.fr/static/images_errata/time4.jpg",
    u"http://errata.ipsl.upmc.fr/static/images_errata/time5.jpg"
]

# Test issue models.
ISSUE_MODELS = [
    u"BADC-CM5A-LR",
    u"BADC-CM5A-MR",
    u"BADC-CM5A-HR",
    u"DKRZ-CM5A-LR",
    u"DKRZ-CM5A-MR",
    u"DKRZ-CM5A-HR",
    u"IPSL-CM5A-LR",
    u"IPSL-CM5A-MR",
    u"IPSL-CM5A-HR"
]

# Test issue variables.
ISSUE_VARIABLES = [
	u"bsi",
	u"dcalc",
	u"pp"
]

# Test issue.
ISSUE = {
    JF_DATASETS: random.sample(ISSUE_DATASETS, 10),
    JF_DATE_CREATED: unicode(dt.datetime.utcnow()),
    JF_DESCRIPTION: unicode(uuid.uuid4()),
    JF_EXPERIMENTS: random.sample(ISSUE_EXPERIMENTS, 2),
    JF_INSTITUTE: random.choice(INSTITUTE)['key'],
    JF_MATERIALS: random.sample(ISSUE_MATERIALS, 3),
    JF_MODELS: random.sample(ISSUE_MODELS, 3),
    JF_PROJECT: random.choice(PROJECT)['key'],
    JF_SEVERITY: random.choice(SEVERITY)['key'],
    JF_STATUS: STATUS_NEW,
    JF_TITLE: unicode(uuid.uuid4()),
    JF_UID: unicode(uuid.uuid4()),
    JF_URL: u"http://errata.ipsl.upmc.fr/issue/1",
    JF_VARIABLES: random.sample(ISSUE_VARIABLES, 2)
    }
