from errata.utils import config


# Email address of moderation list.
ADDRESS_MODERATION = "errata-moderation@es-doc.org"

# On errata accepted -> email body template.
ON_ERRATA_ACCEPTED_EMAIL_BODY_TEMPLATE = "on_accepted.txt"

# On errata accepted -> email subject.
ON_ERRATA_ACCEPTED_EMAIL_SUBJECT = "ES-DOC :: ERRATA :: Moderation Acceptance"

# On errata proposed -> email body template.
ON_ERRATA_PROPOSED_EMAIL_BODY_TEMPLATE = "on_proposed.txt"

# On errata proposed -> email subject.
ON_ERRATA_PROPOSED_EMAIL_SUBJECT = "ES-DOC :: ERRATA :: Proposal Received"

# On errata rejected -> email body template.
ON_ERRATA_REJECTED_EMAIL_BODY_TEMPLATE = "on_rejected.txt"

# On errata rejected -> email subject.
ON_ERRATA_REJECTED_EMAIL_SUBJECT = "ES-DOC :: ERRATA :: Moderation Rejection"

# SMTP server -> host.
SMTP_HOST = config.moderation.smtp_server.host

# SMTP server -> credentials.
SMTP_CREDENTIALS = (
	config.moderation.smtp_server.credentials.user,
	config.moderation.smtp_server.credentials.password
	)

# SMTP server -> SSL port.
SMTP_PORT_SSL = config.moderation.smtp_server.ports.ssl

# SMTP server -> TLS port.
SMTP_PORT_TLS = config.moderation.smtp_server.ports.tls
