#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
    log "DB : inserting test issues ..."
	if [ "$1" ]; then
		python $ERRATA_HOME/jobs/run_db_insert_test_issues.py -d $1
	else
		python $ERRATA_HOME/jobs/run_db_insert_test_issues.py -d $ERRATA_HOME/test-data
	fi
}

# Invoke entry point.
main $1
