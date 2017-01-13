#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Grant db permissions.
_db_grant_permissions()
{
	log "Granting DB permissions"
	psql -U $ERRATA_DB_ADMIN -d $ERRATA_DB_NAME -q -f $ERRATA_WS_HOME/sh/db_permissions.sql
}

# Seed db.
_db_setup()
{
	log "Creating DB objects"
    source $ERRATA_WS_HOME/venv/bin/activate
	python $ERRATA_WS_HOME/sh/db_setup.py
}

# Main entry point.
main()
{
	log "API-DB : setting up ..."

	_db_setup
	# _db_grant_permissions

	log "API-DB : set up"
}

# Invoke entry point.
main
