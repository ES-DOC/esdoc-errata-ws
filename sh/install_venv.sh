#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "installing virtual environment ..."

    $ERRATA_WS_PIP install --upgrade pip
    $ERRATA_WS_PIP install --upgrade virtualenv
    virtualenv $ERRATA_WS_HOME/ops/venv
    source $ERRATA_WS_HOME/sh/activate_venv.sh
    $ERRATA_WS_PIP install --upgrade pip
    $ERRATA_WS_PIP install --upgrade --no-cache-dir -I -r $ERRATA_WS_HOME/resources/requirements.txt
    deactivate
}

# Invoke entry point.
main
