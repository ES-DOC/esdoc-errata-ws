import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from errata.notifications import constants
from errata.notifications import templates


def dispatch_on_accepted(email_address, errata_uid):
	"""Dispatches an email upon acceptance of an errata by a moderator.
	
	:param email_address: Email address of errata proposer.
	:param errata_uid: Unique identifier of proposed errata.

	"""
	body = templates.get_on_accepted_email_body(errata_uid)
	subject = constants.ON_ERRATA_ACCEPTED_EMAIL_SUBJECT
	msg = _get_message(email_address, body, subject)

	_dispatch(msg)


def dispatch_on_proposed(email_address, errata_uid):
	"""Dispatches an email upon proposal of an errata by an anonymous user.
	
	:param email_address: Email address of errata proposer.
	:param errata_uid: Unique identifier of proposed errata.

	"""
	body = templates.get_on_proposed_email_body(errata_uid)
	subject = constants.ON_ERRATA_PROPOSED_EMAIL_SUBJECT
	msg = _get_message(email_address, body, subject)

	_dispatch(msg)


def dispatch_on_rejected(email_address, errata_uid):
	"""Dispatches an email upon rejection of an errata by a moderator.
	
	:param email_address: Email address of errata proposer.
	:param errata_uid: Unique identifier of proposed errata.

	"""
	body = templates.get_on_rejected_email_body(errata_uid)
	subject = constants.ON_ERRATA_REJECTED_EMAIL_SUBJECT
	msg = _get_message(email_address, body, subject)

	_dispatch(msg)


def _dispatch(msg):
	"""Dispatches a message to SMTP server.
	
	"""
	# print(msg)
	# return

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
