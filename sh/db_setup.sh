#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
	log "DB : setting up ..."

    source $ERRATA_WS_HOME/sh/activate_venv.sh
	python $ERRATA_WS_HOME/sh/db_setup.py

	log "DB : set up complete ..."
}

# Invoke entry point.
main