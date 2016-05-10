#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "WEB-SERVICE : running ..."
	python $ERRATA_DIR_WS_JOBS/run_web_service.py
}

# Invoke entry point.
main
