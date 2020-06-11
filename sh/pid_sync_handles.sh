#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
	log "PID : syncing ..."

	pushd $ERRATA_WS_HOME
	pipenv run python $ERRATA_WS_HOME/sh/pid_sync_handles.py

	log "PID : syncing complete ..."
}

# Invoke entry point.
main