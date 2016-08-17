#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
    log "SH : upgrading virtual environment ..."

    source $ERRATA_HOME/venv/bin/activate
    pip install --upgrade pip
    pip install --upgrade -r $ERRATA_HOME/requirements.txt
    deactivate
}

# Invoke entry point.
main