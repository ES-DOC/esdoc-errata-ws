from errata.notifications import constants
from errata.notifications.templates import get_template


def dispatch_on_accepted(errata_uid):
	tmpl = get_template(constants.TMPL_ON_ERRATA_ACCEPTED)

	return tmpl.render({
		"errata_uid": errata_uid
	})


def dispatch_on_proposed(errata_uid):
	tmpl = get_template(constants.TMPL_ON_ERRATA_PROPOSED)

	return tmpl.render({
		"errata_uid": errata_uid
	})


def dispatch_on_rejected(errata_uid):
	tmpl = get_template(constants.TMPL_ON_ERRATA_REJECTED)

	return tmpl.render({
		"errata_uid": errata_uid
	})
