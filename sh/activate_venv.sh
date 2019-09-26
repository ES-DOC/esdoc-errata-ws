#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
	export PYTHONPATH=$ERRATA_WS_HOME:$PYTHONPATH
	venv_path=${ERRATA_WS_VENV:-$ERRATA_WS_HOME/ops/venv}
	source $venv_path/bin/activate
	log "venv activated @ "$venv_path
}

# Invoke entry point.
main
