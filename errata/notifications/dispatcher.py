import smtplib

from errata.notifications import constants
from errata.notifications import templates



HOST = "smtp.de.opalstack.com"
CREDENTIALS = ("errata-moderation", "opalstack@Silence93!")
PORT_SSL = 465
PORT_TLS = 587
SENDER = "errata-moderation@es-doc.org"
RECIEVERS = "asladeofgreen@gmail.com"


def dispatch_on_accepted(email_address, errata_uid):
	email_body = templates.get_on_accepted_template(errata_uid)
	
	_dispatch(email_address, email_body)


def dispatch_on_proposed(email_address, errata_uid):
	email_body = templates.get_on_proposed_template(errata_uid)

	_dispatch(email_address, email_body)


def dispatch_on_rejected(email_address, errata_uid):
	email_body = templates.get_on_rejected_template(errata_uid)

	_dispatch(email_address, email_body)


def _dispatch(email_address, email_body):
	"""Dispatches an email message.
	
	"""
	# Connect over TLS port.
	smtp = smtplib.SMTP(HOST, PORT_TLS)

	# Secure contents with TLS encryption.
	smtp.starttls()

	# Connect.
	smtp.login(CREDENTIALS[0], CREDENTIALS[1])

	# Dispatch email.
	smtp.sendmail(SENDER, [email_address], email_body)

	# Close smtp channel.
	smtp.quit()
