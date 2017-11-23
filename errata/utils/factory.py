# -*- coding: utf-8 -*-
"""
.. module:: utils.factory.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Test issue factory.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import collections
import datetime as dt
import os
import random
import uuid

import pyessv

from errata.utils.config_esg import get_project
from errata.utils.config_esg import get_projects
from errata.utils.constants import PID_ACTION_INSERT
from errata.utils.constants import STATUS_NEW
from errata.utils.constants_json import *
from errata.db.models import Issue
from errata.db.models import IssueFacet
from errata.db.models import PIDServiceTask



# Global now.
_NOW = dt.datetime.utcnow()

# Collection of materials, i.e. supporting images, graphs ... etc.
_MATERIALS = []

# Collection of data set patters used when generating test dataset identifiers.
_DATASETS_PATTERNS = {
    'cmip5': u'cmip5.{}.{}.{}.{}.{}.{}.{}.r1i1p1',
    'cmip6': u'cmip6.{}.{}.{}.{}.r1i1p1f1.{}.clitter.{}',
    'cordex': u'cordex.{}.{}.{}.{}.{}.r12i1p1.{}.v1.{}.{}'
}


def create_issue_dict():
    """Returns a test issue (dictionary encoding).

    """
    cfg = random.choice(get_projects())

    # Date fields to be set server side
    # institute to be extracted from dataset identifiers
    # facets to be extracted from dataset identifiers

    return {
        JF_DATASETS: get_datasets(cfg['canonical_name']),
        JF_DESCRIPTION: unicode(uuid.uuid4()),
        JF_MATERIALS: _get_materials(),
        JF_PROJECT: cfg['canonical_name'],
        JF_SEVERITY: pyessv.get_random('esdoc:errata:severity'),
        JF_STATUS: STATUS_NEW,
        JF_TITLE: unicode(uuid.uuid4()),
        JF_UID: unicode(uuid.uuid4()),
        JF_URLS: [u'https://es-doc.org/cmip6-dataset-errata']
    }


def _get_materials():
    """Returns test affected  datasets.

    """
    if not _MATERIALS:
        fpath = os.getenv('ERRATA_WS_HOME')
        fpath = os.path.join(fpath, 'tests')
        fpath = os.path.join(fpath, 'test-data')
        fpath = os.path.join(fpath, 'materials')
        fpath = os.path.join(fpath, 'MANIFEST.txt')
        with open(fpath, 'r') as fstream:
            for l in [l.strip() for l in fstream.readlines() if l.strip()]:
                _MATERIALS.append(l)

    return _MATERIALS


def get_datasets(project, existing=[]):
    """Returns a collection of test dataset identifiers.

    :param str project: Project code.
    :param list existing: Dataset identifiers to be included in the result.

    :returns: Collection of test datasets.
    :rtype: list

    """
    return [_get_dataset(project) for i in range(5)] + existing


def _get_dataset(project):
    """Returns a dataset identifier.

    """
    pattern = _DATASETS_PATTERNS[project]

    if project == 'cmip5':
        return pattern.format(
            pyessv.get_random('wcrp:cmip5:product'),
            pyessv.parse_namespace('wcrp:cmip5:institute:ipsl'),
            pyessv.get_random('wcrp:cmip5:model'),
            pyessv.get_random('wcrp:cmip5:experiment'),
            pyessv.get_random('wcrp:cmip5:time-frequency'),
            pyessv.get_random('wcrp:cmip5:realm'),
            pyessv.get_random('wcrp:cmip5:cmor-table')
            )

    elif project == 'cmip6':
        return pattern.format(
            pyessv.get_random('wcrp:cmip6:activity-id'),
            pyessv.parse_namespace('wcrp:cmip6:institution-id:ipsl'),
            pyessv.get_random('wcrp:cmip6:source-id'),
            pyessv.get_random('wcrp:cmip6:experiment-id'),
            pyessv.get_random('wcrp:cmip6:table-id'),
            pyessv.get_random('wcrp:cmip6:grid-label')
            )

    elif project == 'cordex':
        return pattern.format(
            pyessv.get_random('wcrp:cordex:product'),
            pyessv.get_random('wcrp:cordex:domain'),
            pyessv.parse_namespace('wcrp:cordex:institute:ipsl-ineris'),
            pyessv.get_random('wcrp:cordex:driving-model'),
            pyessv.get_random('wcrp:cordex:experiment'),
            pyessv.get_random('wcrp:cordex:rcm-name'),
            pyessv.get_random('wcrp:cordex:time-frequency'),
            pyessv.get_random('wcrp:cordex:variable')
            )
