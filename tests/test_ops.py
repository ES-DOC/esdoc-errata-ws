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



# Base API url.
_BASE_URL = os.getenv("ERRATA_API")


def test_heartbeat():
    """ERRATA :: WS :: OPS :: heartbeat.

    """
    # Invoke WS endpoint.
    url = "{}/".format(_BASE_URL)
    r = requests.get(url)

    # Assert WS response.
    tu.assert_ws_response(url, r, fields={'message', 'version'})


def test_verify_authorization():
    """ERRATA :: WS :: OPS :: verify authorization.

    """
    # Invoke WS endpoint.
    url = '{}/verify-authorization'.format(_BASE_URL)
    params = {
        'login': os.getenv("ERRATA_WS_TEST_LOGIN"),
        'institute': os.getenv("ERRATA_WS_TEST_INSTITUTE"),
        'project': os.getenv("ERRATA_WS_TEST_PROJECT"),
        'token': os.getenv("ERRATA_WS_TEST_TOKEN")
    }
    r = requests.get(url, params=params)

    # Assert WS response.
    tu.assert_ws_response(url, r, fields={'message',})
