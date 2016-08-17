#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
    log "SH : installing requirements ..."

    pip install --upgrade -r $ERRATA_HOME/requirements.txt
}

# Invoke entry point.
main
