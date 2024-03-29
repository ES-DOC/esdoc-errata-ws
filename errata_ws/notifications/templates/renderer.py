import os

import jinja2

from errata_ws.notifications import constants


# Set codegen template engine.
_TEMPLATE_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=jinja2.select_autoescape(),
    trim_blocks=True
)


def get_on_accepted_email_body(http_protocol, web_host, errata_uid):
	"""Returns email body to be sent to an anonymous user when a moderator
	   has accepted their errata proposal.

	:param http_protocol: HTTP protocol of web-service serving errata content.
	:param web_host: Host of web-service serving errata content.
	:param errata_uid: Unique identifier of errata being processed.
	:returns: Rendered content for email dispatch.

	"""
	tmpl = _TEMPLATE_ENV.get_template(constants.ON_ERRATA_ACCEPTED_EMAIL_BODY_TEMPLATE)

	return tmpl.render({
		"errata_uid": errata_uid,
		"http_protocol": http_protocol,
		"web_host": web_host
	})


def get_on_proposed_email_body_1(http_protocol, web_host, errata_uid):
	"""Returns body of email to be sent to an anonymous user upon
	submission of an errata proposal.

	:param http_protocol: HTTP protocol of web-service serving errata content.
	:param web_host: Host of web-service serving errata content.
	:param errata_uid: Unique identifier of errata being processed.
	:returns: Rendered content for email dispatch.
	
	"""
	tmpl = _TEMPLATE_ENV.get_template(constants.ON_ERRATA_PROPOSED_EMAIL_BODY_TEMPLATE_1)

	return tmpl.render({
		"errata_uid": errata_uid,
		"http_protocol": http_protocol,
		"web_host": web_host
	})


def get_on_proposed_email_body_2(http_protocol, web_host, address_of_proposer, errata_uid):
	"""Returns body of email to be sent to moderators upon submission of
	an errata proposal by an anonymous user.

	:param http_protocol: HTTP protocol of web-service serving errata content.
	:param web_host: Host of web-service serving errata content.
	:param errata_uid: Unique identifier of errata being processed.
	:param address_of_proposer: Email address of errata proposer.
	:returns: Rendered content for email dispatch.
	
	"""
	tmpl = _TEMPLATE_ENV.get_template(constants.ON_ERRATA_PROPOSED_EMAIL_BODY_TEMPLATE_2)

	return tmpl.render({
		"address_of_proposer": address_of_proposer,
		"errata_uid": errata_uid,
		"http_protocol": http_protocol,
		"web_host": web_host
	})


def get_on_rejected_email_body(http_protocol, web_host, errata_uid):
	"""Returns email body to be sent to an anonymous user when a moderator
	   has rejected their errata proposal.

	:param http_protocol: HTTP protocol of web-service serving errata content.
	:param web_host: Host of web-service serving errata content.
	:param errata_uid: Unique identifier of errata being processed.
	:returns: Rendered content for email dispatch.
	
	"""
	tmpl = _TEMPLATE_ENV.get_template(constants.ON_ERRATA_REJECTED_EMAIL_BODY_TEMPLATE)

	return tmpl.render({
		"errata_uid": errata_uid,
		"http_protocol": http_protocol,
		"web_host": web_host
	})
