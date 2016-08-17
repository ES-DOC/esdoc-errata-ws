#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
    log "SH : installing virtual environment ..."

    pip install --upgrade virtualenv
    virtualenv $ERRATA_HOME/venv
    source $ERRATA_HOME/venv/bin/activate
    pip install --upgrade pip
    pip install --upgrade -r $ERRATA_HOME/requirements.txt
    deactivate
}

# Invoke entry point.
main
