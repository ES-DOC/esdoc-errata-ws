#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "running ..."

	pushd $ERRATA_WS_HOME
	pipenv run python $ERRATA_WS_HOME/sh/app_run.py
	popd
}

# Invoke entry point.
main
