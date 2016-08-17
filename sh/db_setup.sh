#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Grant db permissions.
_db_grant_permissions()
{
	log "Granting DB permissions"
	psql -U esdoc_errata_db_admin -d esdoc_errata -q -f $ERRATA_HOME/sh/db_grant_permissions.sql
}

# Seed db.
_db_setup()
{
	log "Creating DB objects"
    source $ERRATA_HOME/venv/bin/activate
	python $ERRATA_HOME/jobs/run_db_setup.py
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
