#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "DB : creating large database for testing ..."
    source $ERRATA_WS_HOME/venv/bin/activate
	python $ERRATA_WS_HOME/sh/custom/db_create_large_for_testing.py -d $ERRATA_WS_HOME/tests/test-data -c $1
}

# Invoke entry point.
main $1
