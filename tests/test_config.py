# -*- coding: utf-8 -*-

"""
.. module:: test_config_esg.py

   :license: GPL / CeCILL
   :platform: Unix, Windows
   :synopsis: Executes esg configuration integration tests.

.. moduleauthor:: Earth System Documentation (ES-DOC) <dev@es-doc.org>

"""
import pyessv

from errata.utils import config
from errata.utils import config_esg

from tests import utils as tu



# String  types.
_STR_TYPE = (unicode, str)


def test_fields():
    """ERRATA :: WS :: CONFIG :: Web-service config.

    """
    for field, typeof in {
    	('cookie_secret', _STR_TYPE),
    	('db', _STR_TYPE),
    	('host', _STR_TYPE),
    	('apply_security_policy', bool),
    	('mode', _STR_TYPE),
    	('port', int),
    	('validate_issue_urls', bool)
    }:
    	_asset_field(config.__dict__, field, typeof)


def test_fields_pid():
    """ERRATA :: WS :: CONFIG :: PID config.

    """
    _asset_field(config.__dict__, 'pid', object)
    for field, typeof in {
    	('data_node1', _STR_TYPE),
    	('is_test', bool),
    	('prefix', _STR_TYPE),
    	('rabbit_exchange', _STR_TYPE),
    	('rabbit_password_trusted', _STR_TYPE),
    	('rabbit_user_open', _STR_TYPE),
    	('rabbit_user_trusted', _STR_TYPE),
    	('rabbit_urls_open', list),
    	('rabbit_url_trusted', _STR_TYPE),
        ('ssl_enabled', bool),
    	('sync_retry_interval_in_seconds', int),
    	('thredds_service_path1', _STR_TYPE)
    }:
    	_asset_field(config.pid.__dict__, field, typeof)


def test_get_esg_projects():
    """ERRATA :: WS :: Postive Test :: Get ESGF projects (all).

    """
    projects = config_esg.get_projects()
    assert isinstance(projects, list)
    if bool(count):
        assert len(projects) == count
    for project in projects:
        assert isinstance(project, dict)
        for field in {'canonical_name', 'is_pid_client', 'facets'}:
            assert field in project
        for facet in project['facets'].values():
            assert isinstance(facet['collection'], pyessv.Collection)


def test_get_esg_project():
    """ERRATA :: WS :: Postive Test :: Get ESGF project.

    """
    for name in [i['canonical_name'] for i in config_esg.get_projects()]:
        assert isinstance(config_esg.get_project(name), dict)


def _asset_field(cfg, field, typeof):
    """Asserts a configuration field.

    """
    assert field in cfg
    assert isinstance(cfg[field], typeof)
