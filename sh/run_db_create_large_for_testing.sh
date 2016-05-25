#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "DB : creating large database for testing ..."
	python $ERRATA_DIR_WS_JOBS/run_db_create_large_for_testing.py -d $ERRATA_DIR_TEST_DATA -c $1
}

# Invoke entry point.
main $1
