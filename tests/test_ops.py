# -*- coding: utf-8 -*-

"""
.. module:: test_ops.py

   :license: GPL / CeCILL
   :platform: Unix, Windows
   :synopsis: Executes web-service operations (ops) endpoint tests.

.. moduleauthor:: Earth System Documentation (ES-DOC) <dev@es-doc.org>

"""
import os

import requests

from tests import utils as tu



# Set of target urls.
_URL_HEARTBEAT = "{}/".format(os.getenv("ERRATA_API"))

print 777, _URL_HEARTBEAT


def test_heartbeat():
    """ERRATA :: WS :: Postive Test :: Ops heartbeat.

    """
    # Invoke WS endpoint.
    url = _URL_HEARTBEAT
    r = requests.get(_URL_HEARTBEAT)

    # Assert WS response.
    data = tu.assert_ws_response(url, r)
    assert "message" in data
    assert "version" in data


def test_credentials():
    """ERRATA :: WS :: Postive Test :: Ops heartbeat.

    """
    # Invoke WS endpoint.
    url = _URL_HEARTBEAT
    r = requests.get(_URL_HEARTBEAT)

    # Assert WS response.
    data = tu.assert_ws_response(url, r)
    assert "message" in data
    assert "version" in data