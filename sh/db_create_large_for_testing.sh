#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
    log "DB : creating large database for testing ..."
    source $ERRATA_HOME/venv/bin/activate
	python $ERRATA_HOME/sh/db_create_large_for_testing.py -d $ERRATA_HOME/tests/test-data -c $1
}

# Invoke entry point.
main $1
