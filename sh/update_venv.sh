#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
	source $ERRATA_WS_HOME/sh/activate_venv.sh
    pip install --upgrade pip
    pip install --upgrade --no-cache-dir -I -r $ERRATA_WS_HOME/requirements.txt

    deactivate

    log "virtual environment updated"
}

# Invoke entry point.
main
