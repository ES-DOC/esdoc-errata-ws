#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "DB : creating large database ..."

    pushd $ERRATA_WS_HOME
	pipenv run python $ERRATA_WS_HOME/sh/db_create_large_for_testing.py -c $1

    log "DB : creating large database complete ..."
}

# Invoke entry point.
main $1
