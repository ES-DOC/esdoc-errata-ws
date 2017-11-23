# -*- coding: utf-8 -*-
"""
.. module:: write_vocabs.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Writes ES-DOC errata vocabularies to file system.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
import arrow

import pyessv



# Ensure we use fixed creation date.
_CREATE_DATE = arrow.get('2017-06-21 00:00:00.000000+0000').datetime



def _main():
    """Main entry point.

    """
    authority = _write_authority()
    scope = _write_scope(authority)
    for func in (
        _write_projects,
        _write_severity,
        _write_status
        ):
        func(scope)

    # Add to archive & persist to file system.
    pyessv.add(authority)
    pyessv.save()


def _write_authority():
    """Writes ES-DOC authority.

    """
    return pyessv.load('esdoc') or pyessv.create_authority(
        'esdoc',
        'Earth System Documentation',
        label='ES-DOC',
        url='https://es-doc.org',
        create_date=_CREATE_DATE
        )


def _write_scope(authority):
    """Writes ES-DOC errata scope.

    """
    return pyessv.load('esdoc:errata') or pyessv.create_scope(authority,
        'errata',
        'Controlled Vocabularies (CVs) for use in dataset errata',
        label='Dataset Errata',
        url='https://github.com/ES-DOC/esdoc-errata-ws',
        create_date=_CREATE_DATE
        )


def _write_status(scope):
    """Writes ES-DOC errata status terms.

    """
    collection = pyessv.create_collection(scope, 'status',
        label='Status',
        description="Errata status codes"
    )

    pyessv.create_term(collection, 'new',
        label='New',
        data={
            'color': '#00ff00'
        }
    )

    pyessv.create_term(collection, 'onhold',
        label='On Hold',
        data={
            'color': '#ff9900'
        }
    )

    pyessv.create_term(collection, 'resolved',
        label='Resolved',
        data={
            'color': '#0c343d'
        }
    )
    pyessv.create_term(collection, 'wontfix',
        label='Wont Fix',
        data={
            'color': '#38761d'
        }
    )

def _write_severity(scope):
    """Writes ES-DOC errata severity terms.

    """
    collection = pyessv.create_collection(scope, 'severity',
        label='Severity',
        description="Errata severity codes"
    )

    pyessv.create_term(collection, 'low',
        label='Low',
        data={
            'color': '#e6b8af',
            'sortOrdinal': 0
        }
    )

    pyessv.create_term(collection, 'medium',
        label='Medium',
        data={
            'color': '#dd7e6b',
            'sortOrdinal': 1
        }
    )

    pyessv.create_term(collection, 'high',
        label='High',
        data={
            'color': '#cc4125',
            'sortOrdinal': 2
        }
    )

    pyessv.create_term(collection, 'critical',
        label='Critical',
        data={
            'color': '#a61c00',
            'sortOrdinal': 3
        }
    )


def _write_projects(scope):
    """Writes ES-DOC errata project terms.

    """
    collection = pyessv.create_collection(scope, 'project',
        label='Project',
        description="Errata supported project codes"
    )

    pyessv.create_term(collection, 'cmip5',
        label='CMIP5',
        data={
            "facets": [
                "wcrp:cmip5:institute",
                "wcrp:cmip5:experiment",
                "wcrp:cmip5:model",
                "wcrp:cmip5:variable"
            ],
            "is_pid_client": False
        }
    )

    pyessv.create_term(collection, 'cmip6',
        label='CMIP6',
        data={
            "facets": [
                "wcrp:cmip6:institution-id",
                "wcrp:cmip6:experiment-id",
                "wcrp:cmip6:source-id",
                "wcrp:cmip6:variable"
            ],
            "is_pid_client": True
        }
    )

    pyessv.create_term(collection, 'cordex',
        label='CORDEX',
        data={
            "facets": [
                "wcrp:cordex:institute",
                "wcrp:cordex:experiment",
                "wcrp:cordex:rcm-model",
                "wcrp:cordex:variable"
            ],
            "is_pid_client": False
        }
    )


# Entry point.
if __name__ == '__main__':
    _main()
