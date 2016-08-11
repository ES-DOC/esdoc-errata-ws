#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
    log "WEB-SERVICE : running ..."

	python2.7 $ERRATA_HOME/jobs/run_web_service.py
}

# Invoke entry point.
main
