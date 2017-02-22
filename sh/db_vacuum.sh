#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
	log "DB : vacuuming ..."

	psql -U $ERRATA_DB_ADMIN -d $ERRATA_DB_NAME -q -f $ERRATA_WS_HOME/sh/db_vacuum.sql

	log "DB : vacuuming complete"
}

# Invoke entry point.
main
