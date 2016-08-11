#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
    log "DB : ingesting issues from remote GitHub repos ..."
	python2.7 $ERRATA_HOME/jobs/run_db_ingest.py
}

# Invoke entry point.
main
