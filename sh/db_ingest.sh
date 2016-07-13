#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "DB : ingesting issues from remote GitHub repos ..."
	/usr/local/bin/python2.7 $ERRATA_DIR_WS_JOBS/run_db_ingest.py
}

# Invoke entry point.
main
