# -*- coding: utf-8 -*-

"""
.. module:: test_config_esg.py

   :license: GPL / CeCILL
   :platform: Unix, Windows
   :synopsis: Executes esg configuration integration tests.

.. moduleauthor:: Earth System Documentation (ES-DOC) <dev@es-doc.org>

"""
import pyessv

from errata.utils import config_esg as config



def test_get_projects():
    """ERRATA :: WS :: Postive Test :: Get all projects.

    """
    projects = config.get_projects()
    assert isinstance(projects, list)
    for project in projects:
        assert isinstance(project, dict)
        for field in {'canonical_name', 'is_active', 'is_pid_client', 'facets'}:
            assert field in project
        for facet in project['facets'].values():
            assert isinstance(facet['collection'], (type(None), pyessv.Collection))


def test_get_project():
    """ERRATA :: WS :: Postive Test :: Get project.

    """
    for name in [i['canonical_name'] for i in config.get_projects()]:
        assert isinstance(config.get_project(name), dict)


def test_get_active_project():
    """ERRATA :: WS :: Postive Test :: Get active projects.

    """
    assert len(config.get_active_projects()) == 2
