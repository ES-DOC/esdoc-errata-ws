#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
    log $(which python)
    log "DB : creating large database for testing ..."
	python2.7 $ERRATA_HOME/jobs/run_db_create_large_for_testing.py -d $ERRATA_HOME/test-data -c $1
}

# Invoke entry point.
main $1