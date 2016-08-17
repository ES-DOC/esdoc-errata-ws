#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Create db users.
_db_create_users()
{
	log "Creating DB users"
	createuser -U postgres -d -s esdoc_errata_db_admin
	createuser -U esdoc_errata_db_admin -D -S -R esdoc_errata_db_user
}

# Create db.
_db_create()
{
	log "Creating DB"
	createdb -U esdoc_errata_db_admin -e -O esdoc_errata_db_admin -T template0 esdoc_errata
}

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
	$ERRATA_PYTHON $ERRATA_HOME/jobs/run_db_setup.py
}

# Main entry point.
main()
{
	log "API-DB : installing ..."

	_db_create_users
	_db_create
	_db_setup
	_db_grant_permissions

	log "API-DB : installed"
}

# Invoke entry point.
main
