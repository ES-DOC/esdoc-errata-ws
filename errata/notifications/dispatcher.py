import smtplib

from errata.notifications import constants
from errata.notifications import templates


def dispatch_on_accepted(errata_uid):
	email_body = templates.get_on_accepted_template(errata_uid)

	return email_body


def dispatch_on_proposed(errata_uid):
	email_body = templates.get_on_proposed_template(errata_uid)

	return email_body


def dispatch_on_rejected(errata_uid):
	email_body = templates.get_on_rejected_template(errata_uid)

	return email_body
