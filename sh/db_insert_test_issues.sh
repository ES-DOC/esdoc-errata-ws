#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "DB : inserting test issues ..."
	if [ "$1" ]; then
		python $ERRATA_DIR_WS_JOBS/run_db_insert_test_issues.py -d $1
	else
		python $ERRATA_DIR_WS_JOBS/run_db_insert_test_issues.py -d $ERRATA_DIR_TEST_DATA
	fi
}

# Invoke entry point.
main $1
