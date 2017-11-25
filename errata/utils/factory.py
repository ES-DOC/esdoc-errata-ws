# -*- coding: utf-8 -*-
"""
.. module:: utils.factory.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Test issue factory.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import datetime as dt
import uuid

import pyessv

from errata.utils.constants import *



# Global now.
_NOW = dt.datetime.utcnow()

# Collection of materials, i.e. supporting images, graphs ... etc.
_MATERIALS = []

# Collection of data set patters used when generating test dataset identifiers.
_DATASETS_PATTERNS = {
    'cmip5': u'cmip5.{}.{}.{}.{}.{}.{}.{}.r1i1p1#v20180101',
    'cmip6': u'cmip6.{}.{}.{}.{}.r1i1p1f1.{}.Emon.{}#v20180101',
    'cordex': u'cordex.{}.{}.{}.{}.{}.r12i1p1.{}.v1.{}.{}#v20180101'
}


def create_issue_dict():
    """Returns a test issue (dictionary encoding).

    """
    project_id = pyessv.get_random('esdoc:errata:project')

    return {
        JF_DATASETS: get_datasets(project_id),
        JF_DESCRIPTION: unicode(uuid.uuid4()),
        JF_MATERIALS: _get_materials(),
        JF_PROJECT: project_id,
        JF_SEVERITY: pyessv.get_random('esdoc:errata:severity'),
        JF_STATUS: STATUS_ON_HOLD,
        JF_TITLE: unicode(uuid.uuid4()),
        JF_UID: unicode(uuid.uuid4()),
        JF_URLS: ['https://es-doc.org/cmip6-dataset-errata']
    }


def _get_materials():
    """Returns test affected  datasets.

    """
    return [
        'https://test-errata.es-doc.org/media/img/materials/material-01.png',
        'https://test-errata.es-doc.org/media/img/materials/material-02.png',
        'https://test-errata.es-doc.org/media/img/materials/material-03.png',
        'https://test-errata.es-doc.org/media/img/materials/material-04.png',
        'https://test-errata.es-doc.org/media/img/materials/material-05.png'
    ]


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
