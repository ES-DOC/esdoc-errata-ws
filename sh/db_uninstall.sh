#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/utils.sh

# Create db users.
_db_drop_users()
{
	log "Deleting DB users"

	dropuser -U esdoc_errata_db_admin esdoc_errata_db_user
	dropuser -U postgres esdoc_errata_db_admin
}

# Drop db.
_db_drop()
{
	log "Dropping DB"

	dropdb -U esdoc_errata_db_admin esdoc_errata
}

# Main entry point.
main()
{
	log "DB : uninstalling ..."
	_db_drop
	_db_drop_users
	log "DB : uninstalled"
}

# Invoke entry point.
main
