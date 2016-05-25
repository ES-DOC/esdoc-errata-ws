#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "SH : installing requirements ..."
    pip install -r $ERRATA_HOME/requirements.txt
}

# Invoke entry point.
main
