import datetime as dt
import uuid

import pyessv

from errata_ws.utils.constants import *



# Global now.
_NOW = dt.datetime.utcnow()

# Collection of materials, i.e. supporting images, graphs ... etc.
_MATERIALS = []

# Collection of data set patters used when generating test dataset identifiers.
_DATASETS_PATTERNS = {
    'cmip5': u'cmip5.{}.{}.{}.{}.{}.{}.{}.r1i1p1#20180101',
    'cmip6': u'CMIP6.{}.{}.{}.{}.r1i1p1f1.{}.Emon.{}#20180101',
    'cordex': u'cordex.{}.{}.{}.{}.{}.r12i1p1.{}.v1.{}.{}#20180101'
}


def create_issue_dict():
    """Returns a test issue (dictionary encoding).

    """
    project_id = pyessv.load_random('esdoc:errata:project')

    return {
        JF_DATASETS: get_datasets(project_id),
        JF_DESCRIPTION: unicode(uuid.uuid4()),
        JF_MATERIALS: _get_materials(),
        JF_PROJECT: project_id,
        JF_SEVERITY: pyessv.load_random('esdoc:errata:severity'),
        JF_STATUS: ISSUE_STATUS_NEW,
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
            pyessv.load_random('wcrp:cmip5:product', field='raw_name'),
            pyessv.parse('wcrp:cmip5:institute:ipsl', field='raw_name'),
            pyessv.load_random('wcrp:cmip5:model', field='raw_name'),
            pyessv.load_random('wcrp:cmip5:experiment', field='raw_name'),
            pyessv.load_random('wcrp:cmip5:time-frequency', field='raw_name'),
            pyessv.load_random('wcrp:cmip5:realm', field='raw_name'),
            pyessv.load_random('wcrp:cmip5:cmor-table', field='raw_name')
            )

    elif project == 'cmip6':
        return pattern.format(
            pyessv.load_random('wcrp:cmip6:activity-id', field='raw_name'),
            pyessv.parse('wcrp:cmip6:institution-id:ipsl', field='raw_name'),
            pyessv.load_random('wcrp:cmip6:source-id', field='raw_name'),
            pyessv.load_random('wcrp:cmip6:experiment-id', field='raw_name'),
            pyessv.load_random('wcrp:cmip6:table-id', field='raw_name'),
            pyessv.load_random('wcrp:cmip6:grid-label', field='raw_name')
            )

    elif project == 'cordex':
        return pattern.format(
            pyessv.load_random('wcrp:cordex:product', field='raw_name'),
            pyessv.load_random('wcrp:cordex:domain', field='raw_name'),
            pyessv.parse('wcrp:cordex:institute:ipsl-ineris', field='raw_name'),
            pyessv.load_random('wcrp:cordex:driving-model', field='raw_name'),
            pyessv.load_random('wcrp:cordex:experiment', field='raw_name'),
            pyessv.load_random('wcrp:cordex:rcm-name', field='raw_name'),
            pyessv.load_random('wcrp:cordex:time-frequency', field='raw_name'),
            pyessv.load_random('wcrp:cordex:variable', field='raw_name')
            )
