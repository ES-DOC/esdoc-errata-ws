#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "installing virtual environment ..."

    pip install --upgrade pip
    pip install --upgrade virtualenv
    virtualenv $ERRATA_WS_HOME/ops/venv
    source $ERRATA_WS_HOME/sh/activate_venv.sh
    pip install --upgrade pip
    pip install --upgrade --no-cache-dir -I -r $ERRATA_WS_HOME/requirements.txt

    deactivate
}

# Invoke entry point.
main
