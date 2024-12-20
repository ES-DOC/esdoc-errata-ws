from errata_ws.utils import config


# Email address of moderation list.
ADDRESS_MODERATION = "moderation@errata.ipsl.fr"

# On errata accepted -> email body template.
ON_ERRATA_ACCEPTED_EMAIL_BODY_TEMPLATE = "on_accepted.txt"

# On errata accepted -> email subject.
ON_ERRATA_ACCEPTED_EMAIL_SUBJECT = "ERRATA :: Moderation Acceptance"

# On errata proposed -> email body template 1.
ON_ERRATA_PROPOSED_EMAIL_BODY_TEMPLATE_1 = "on_proposed_1.txt"

# On errata proposed -> email body template 2.
ON_ERRATA_PROPOSED_EMAIL_BODY_TEMPLATE_2 = "on_proposed_2.txt"

# On errata proposed -> email subject.
ON_ERRATA_PROPOSED_EMAIL_SUBJECT = "ERRATA :: Proposal Received"

# On errata rejected -> email body template.
ON_ERRATA_REJECTED_EMAIL_BODY_TEMPLATE = "on_rejected.txt"

# On errata rejected -> email subject.
ON_ERRATA_REJECTED_EMAIL_SUBJECT = "ERRATA :: Moderation Rejection"

# SMTP server -> host.
SMTP_HOST = "localhost"

# SMTP server -> credentials.
SMTP_CREDENTIALS = (
	config.moderation.smtp_server.credentials.user,
	config.moderation.smtp_server.credentials.password
	)

# SMTP server -> SSL port.
SMTP_PORT_SSL = config.moderation.smtp_server.ports.ssl

# SMTP server -> TLS port.
SMTP_PORT_TLS = 25
