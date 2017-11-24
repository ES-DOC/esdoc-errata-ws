#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
	source $ERRATA_WS_HOME/sh/activate_venv.sh
    $ERRATA_WS_PIP install --upgrade pip
    $ERRATA_WS_PIP install --upgrade --no-cache-dir -I -r $ERRATA_WS_HOME/resources/requirements.txt
    $ERRATA_WS_PIP install --upgrade --no-cache-dir -I -r $ERRATA_WS_HOME/resources/requirements-pyesdoc.txt

    deactivate

    log "virtual environment updated"
}

# Invoke entry point.
main
