import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from errata.notifications import constants
from errata.notifications import templates


def dispatch_on_accepted(address_of_proposer, errata_uid):
	"""Dispatches an email upon acceptance of an errata by a moderator.
	
	:param address_of_proposer: Email address of errata proposer.
	:param errata_uid: Unique identifier of errata being processed.

	"""
	body = templates.get_on_accepted_email_body(errata_uid)
	subject = constants.ON_ERRATA_ACCEPTED_EMAIL_SUBJECT
	msg = _get_message(address_of_proposer, body, subject)

	_dispatch(msg)


def dispatch_on_proposed(address_of_proposer, errata_uid):
	"""Dispatches an email upon proposal of an errata by an anonymous user.
	
	:param address_of_proposer: Email address of errata proposer.
	:param errata_uid: Unique identifier of errata being processed.

	"""
	body = templates.get_on_proposed_email_body(errata_uid)
	subject = constants.ON_ERRATA_PROPOSED_EMAIL_SUBJECT
	msg = _get_message(address_of_proposer, body, subject)

	_dispatch(msg)


def dispatch_on_rejected(address_of_proposer, errata_uid):
	"""Dispatches an email upon rejection of an errata by a moderator.
	
	:param address_of_proposer: Email address of errata proposer.
	:param errata_uid: Unique identifier of errata being processed.

	"""
	body = templates.get_on_rejected_email_body(errata_uid)
	subject = constants.ON_ERRATA_REJECTED_EMAIL_SUBJECT
	msg = _get_message(address_of_proposer, body, subject)

	_dispatch(msg)


def _dispatch(msg):
	"""Dispatches a message to SMTP server.
	
	"""
	# Open channel over TLS port.
	smtp = smtplib.SMTP(constants.SMTP_HOST, constants.SMTP_PORT_TLS)

	# Secure contents with TLS encryption.
	smtp.starttls()

	# Authenticate.
	smtp.login(constants.SMTP_CREDENTIALS[0], constants.SMTP_CREDENTIALS[1])

	# Dispatch.
	smtp.sendmail(constants.ADDRESS_MODERATION, msg["To"], msg.as_string())
	
	# Close channel.
	smtp.quit()


def _get_message(address, body, subject):
	"""Returns formatted message ready for dispatch.
	
	"""
	msg = MIMEMultipart()
	msg["From"] = constants.ADDRESS_MODERATION
	msg["To"] = address
	msg["Subject"] = subject
	msg.attach(MIMEText(body))

	return msg
