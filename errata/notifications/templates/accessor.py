import os

import jinja2

from errata.notifications import constants


# Set codegen template engine.
_TEMPLATE_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=jinja2.select_autoescape(),
    trim_blocks=True
)


def get_on_accepted_email_body(errata_uid):
	tmpl = _TEMPLATE_ENV.get_template(constants.ON_ERRATA_ACCEPTED_EMAIL_BODY_TEMPLATE)

	return tmpl.render({
		"errata_uid": errata_uid
	})


def get_on_proposed_email_body(errata_uid):
	tmpl = _TEMPLATE_ENV.get_template(constants.ON_ERRATA_PROPOSED_EMAIL_BODY_TEMPLATE)

	return tmpl.render({
		"errata_uid": errata_uid
	})


def get_on_rejected_email_body(errata_uid):
	tmpl = _TEMPLATE_ENV.get_template(constants.ON_ERRATA_REJECTED_EMAIL_BODY_TEMPLATE)

	return tmpl.render({
		"errata_uid": errata_uid
	})
