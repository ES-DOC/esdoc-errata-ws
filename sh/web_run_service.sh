#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "WEB-SERVICE : running ..."
	/usr/local/bin/python2.7 $ERRATA_DIR_WS_JOBS/run_web_service.py
}

# Invoke entry point.
main
