# -*- coding: utf-8 -*-

"""
.. module:: test_publishing.py

   :license: GPL / CeCILL
   :platform: Unix, Windows
   :synopsis: Executes web-service publishing endpoint tests.

.. moduleauthor:: Earth System Documentation (ES-DOC) <dev@es-doc.org>

"""
import json
import os
import uuid

import requests

from errata.utils import constants
from errata.utils import utests as tu



# Test issue uid.
_ISSUE_UID = unicode(uuid.uuid4())

# Test issue.
_ISSUE = {
	'description': unicode(uuid.uuid4()),
	'institute': constants.INSTITUTE_IPSL,
	'materials': [
        "http://errata.ipsl.upmc.fr/static/images_errata/time.jpg",
        "http://errata.ipsl.upmc.fr/static/images_errata/time5.jpg"
	],
	'models': [],
	'severity': constants.SEVERITY_LOW,
	'project': u"CMIP5",
	'title': unicode(uuid.uuid4()),
	'id': _ISSUE_UID,
	'url': u"http://errata.ipsl.upmc.fr/issue/1",
	'workflow': constants.WORKFLOW_NEW,
	'datasets': [
		"cmip5.output1.IPSL.IPSL-CM5A-LR.1pctCO2.yr.ocnBgchem.Oyr.r2i1p1#20161010",
		"cmip5.output1.IPSL.IPSL-CM5A-LR.1pctCO2.yr.ocnBgchem.Oyr.r1i1p1#20161010",
		"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r10i1p1#20110922",
		"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r11i1p1#20110901",
		"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r12i1p1#20110901",
		"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r1i1p1#20110901",
		"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r1i1p1#20130322",
		"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r2i1p1#20110901",
		"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r3i1p1#20110901",
		"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r4i1p1#20110901",
		"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r6i1p1#20110901",
		"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r7i1p1#20110901",
		"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r8i1p1#20110901",
		"cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r9i1p1#20110901"
		]
	}

# Test issue - JSON representation.
_ISSUE_JSON = json.dumps(_ISSUE)

# Set of target urls.
_URL = os.getenv("ERRATA_API")
_URL_POST = "{}/1/issue/create".format(_URL)
_URL_PUT = "{}/1/issue/update".format(_URL)
_URL_GET = "{}/1/issue/retrieve".format(_URL)
_URL_GET_PARAMS = "?id={}"
_URL_CLOSE = "{}1/issue/close".format(_URL)
_URL_CLOSE_PARAMS = "?id={}"


def test_publish():
	"""ERRATA :: WS :: Test publishing an issue.

	"""
	# Post issue to web-service.
	response = requests.post(
		_URL_POST,
		data=_ISSUE_JSON,
		headers={'Content-Type': 'application/json'}
		)

	assert response.status_code == requests.codes.OK


# def _test_retrieve(encoding):
# 	"""Tests retrieving a specific document encoding."""
# 	params = _URL_GET_PARAMS.format(encoding, _ISSUE.meta.id, _ISSUE.meta.version)
# 	url = "{}{}".format(_URL_GET, params)
# 	response = requests.get(url)
# 	assert response.status_code == requests.codes.OK

# 	if encoding != 'html':
# 		doc = pyesdoc.decode(response.text, encoding)
# 		assert doc.meta.id == _ISSUE.meta.id
# 		assert doc.meta.version == _ISSUE.meta.version
# 		if pyesdoc.encode(_ISSUE, encoding) != response.text:
# 			pass
# 			# assert pyesdoc.encode(_ISSUE, encoding) == response.text


# def test_retrieve():
# 	"""ERRATA :: WS :: Test retrieving a previously published document.

# 	"""
# 	for encoding in pyesdoc.ENCODINGS_HTTP:
# 		tu.init(_test_retrieve, 'retrieval', suffix=encoding)
# 		yield _test_retrieve, encoding


# def test_republish():
# 	"""ERRATA :: WS :: Test republishing a document.

# 	"""
# 	_ISSUE.rationale = "to restate the bleeding obvious"
# 	_ISSUE.meta.version += 1

# 	data = pyesdoc.encode(_ISSUE, 'json')
# 	headers = {'Content-Type': 'application/json'}
# 	url = _URL_PUT
# 	response = requests.put(url, data=data, headers=headers)
# 	assert response.status_code == requests.codes.OK

# 	params = _URL_GET_PARAMS.format('json', _ISSUE.meta.id, _ISSUE.meta.version)
# 	url = "{}{}".format(_URL_GET, params)
# 	response = requests.get(url)
# 	assert response.status_code == requests.codes.OK

# 	doc = pyesdoc.decode(response.text, 'json')
# 	assert doc.meta.id == _ISSUE.meta.id
# 	assert doc.meta.version == _ISSUE.meta.version
# 	assert doc.rationale == "to restate the bleeding obvious"


# def test_unpublish():
# 	"""ERRATA :: WS :: Test unpublishing a document.

# 	"""
# 	params = _URL_DELETE_PARAMS.format(_ISSUE.meta.id, _ISSUE.meta.version)
# 	url = "{}{}".format(_URL_DELETE, params)
# 	response = requests.delete(url)
# 	assert response.status_code == requests.codes.OK

# 	params = _URL_DELETE_PARAMS.format(_ISSUE.meta.id, _ISSUE.meta.version - 1)
# 	url = "{}{}".format(_URL_DELETE, params)
# 	response = requests.delete(url)
# 	assert response.status_code == requests.codes.OK

