#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Create db users.
_db_create_users()
{
	log "Creating DB users"
	createuser -U $ERRATA_DB_SYSTEM_USER -d -s $ERRATA_DB_ADMIN
	createuser -U $ERRATA_DB_ADMIN -D -S -R $ERRATA_DB_USER
}

# Create db.
_db_create()
{
	log "Creating DB"
	createdb -U $ERRATA_DB_ADMIN -e -O $ERRATA_DB_ADMIN -T template0 $ERRATA_DB_NAME
}

# Grant db permissions.
_db_grant_permissions()
{
	log "Granting DB permissions"
	psql -U $ERRATA_DB_ADMIN -d $ERRATA_DB_NAME -q -f $ERRATA_WS_HOME/sh/db_permissions.sql
}

# Seed db.
_db_setup()
{
    source $ERRATA_WS_HOME/sh/db_setup.sh
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
