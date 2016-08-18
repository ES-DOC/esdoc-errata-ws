#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
    log "WEB-SERVICE : running ..."

    source $ERRATA_HOME/venv/bin/activate
	python $ERRATA_HOME/sh/web_run_service.py
}

# Invoke entry point.
main
