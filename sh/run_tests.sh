#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "ERRATA-TESTS : running ..."

    nosetests -v -s $ERRATA_WS_HOME/tests

    log "ERRATA-TESTS : complete ..."
}

# Invoke entry point.
main
