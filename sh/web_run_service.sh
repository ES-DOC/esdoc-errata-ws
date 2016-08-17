#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
    log "WEB-SERVICE : running ..."

	$ERRATA_PYTHON $ERRATA_HOME/jobs/run_web_service.py
}

# Invoke entry point.
main
