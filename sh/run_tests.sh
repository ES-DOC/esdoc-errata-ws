#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "ERRATA-TESTS : execution starts ..."

    nosetests -v -s $ERRATA_WS_HOME/tests

    log "ERRATA-TESTS : execution complete ..."
}

# Invoke entry point.
main
