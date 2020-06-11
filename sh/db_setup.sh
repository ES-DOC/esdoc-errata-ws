#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
	log "DB : setting up ..."

	pushd $ERRATA_WS_HOME
	pipenv run python $ERRATA_WS_HOME/sh/db_setup.py

	log "DB : set up complete ..."
}

# Invoke entry point.
main