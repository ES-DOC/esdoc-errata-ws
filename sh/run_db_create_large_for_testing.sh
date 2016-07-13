#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/utils.sh

# Main entry point.
main()
{
    log $(which python)
    log "DB : creating large database for testing ..."
	/usr/local/bin/python2.7 $ERRATA_DIR_WS_JOBS/run_db_create_large_for_testing.py -d $ERRATA_DIR_TEST_DATA -c $1
}

# Invoke entry point.
main $1
