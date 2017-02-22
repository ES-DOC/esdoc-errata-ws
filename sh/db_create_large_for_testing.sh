#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "DB : creating large database ..."

    source $ERRATA_WS_HOME/sh/activate_venv.sh
	python $ERRATA_WS_HOME/sh/db_create_large_for_testing.py -d $ERRATA_WS_HOME/tests/test-data -c $1

    log "DB : creating large database complete ..."
}

# Invoke entry point.
main $1
