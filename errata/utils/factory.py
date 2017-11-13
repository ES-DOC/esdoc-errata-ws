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

from errata.utils.config_esg import get_active_project
from errata.utils.config_esg import get_active_projects
from errata.utils.constants import PID_ACTION_INSERT
from errata.utils.constants import SEVERITY
from errata.utils.constants import STATUS_NEW
from errata.utils.constants_json import *
from errata.utils.constants_json import JF_FACET_TYPE_MAP
from errata.db.models import Issue
from errata.db.models import IssueFacet
from errata.db.models import PIDServiceTask



# Global now.
_NOW = dt.datetime.utcnow()

# Collection of materials, i.e. supporting images, graphs ... etc.
_MATERIALS = []

# Collection of data set patters used when generating test dataset identifiers.
_DATASETS_PATTERNS = {
    'cmip5': u'cmip5.output.{}.{}.{}.{}.{}.{}.r1i1p1.v20120602',
    'cmip6': u'cmip6.output.{}.{}.{}.{}.{}.amon.r1i1p1.v20120602',
    'cordex': u'cordex.output.{}.{}.{}.{}.r12i1p1.{}.v1.{}.{}'
}


def create_issue_dict():
    """Returns a test issue (dictionary encoding).

    """
    cfg = random.choice(get_active_projects())

    return {
        JF_DATASETS: get_datasets(cfg['canonical_name']),
        JF_DATE_CREATED: unicode(_NOW),
        JF_DESCRIPTION: unicode(uuid.uuid4()),
        JF_INSTITUTE: u'ipsl',
        JF_MATERIALS: _get_materials(),
        JF_PROJECT: cfg['canonical_name'],
        JF_SEVERITY: random.choice(SEVERITY)['key'],
        JF_STATUS: STATUS_NEW,
        JF_TITLE: unicode(uuid.uuid4()),
        JF_UID: unicode(uuid.uuid4()),
        JF_URLS: [u'https://es-doc.org/cmip6-dataset-errata'],
        JF_FACETS: _get_facets(cfg)
    }


def _get_facets(cfg):
    """Returns map of facet types to facet values.

    """
    result = collections.defaultdict(list)
    for facet_type in cfg['facets']:
        collection = cfg['facets'][facet_type]['collection']
        if len(collection) > 0:
            count = random.randint(1, len(collection))
            if count > 3:
                count = 3
            terms = [i.canonical_name for i in random.sample(collection, count)]
        else:
            terms = [unicode(uuid.uuid4()).split('-')[0] for _ in range(5)]
        result[facet_type] = terms

    return result


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

    if project == 'cordex':
        return pattern.format(
            pyessv.get_random_term('esgf-publisher:cordex:domain'),
            pyessv.get_random_term('esgf-publisher:cordex:institute'),
            pyessv.get_random_term('esgf-publisher:cordex:driving-model'),
            pyessv.get_random_term('esgf-publisher:cordex:experiment'),
            pyessv.get_random_term('esgf-publisher:cordex:rcm-model'),
            pyessv.get_random_term('esgf-publisher:cordex:time-frequency'),
            pyessv.get_random_term('esgf-publisher:cordex:variable')
            )

    elif project == 'cmip5':
        return pattern.format(
            pyessv.get_random_term('wcrp:cmip6:institution-id'),
            pyessv.get_random_term('esgf-publisher:cmip5:model'),
            pyessv.get_random_term('esgf-publisher:cmip5:experiment'),
            pyessv.get_random_term('esgf-publisher:cmip5:time-frequency'),
            pyessv.get_random_term('esgf-publisher:cmip5:realm'),
            pyessv.get_random_term('wcrp:cmip6:table-id')
            )

    elif project == 'cmip6':
        return pattern.format(
            pyessv.get_random_term('wcrp:cmip6:institution-id'),
            pyessv.get_random_term('wcrp:cmip6:source-id'),
            pyessv.get_random_term('wcrp:cmip6:experiment-id'),
            pyessv.get_random_term('wcrp:cmip6:frequency'),
            pyessv.get_random_term('wcrp:cmip6:realm'),
            pyessv.get_random_term('wcrp:cmip6:table-id')
            )
