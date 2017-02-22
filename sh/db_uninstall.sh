#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Create db users.
_db_drop_users()
{
	log "Deleting DB users"

	dropuser -U $ERRATA_DB_ADMIN $ERRATA_DB_USER
	dropuser -U postgres $ERRATA_DB_ADMIN
}

# Drop db.
_db_drop()
{
	log "Dropping DB"

	dropdb -U $ERRATA_DB_ADMIN esdoc_errata
}

# Main entry point.
main()
{
	log "DB : uninstalling ..."

	_db_drop
	_db_drop_users

	log "DB : uninstall complete"
}

# Invoke entry point.
main
