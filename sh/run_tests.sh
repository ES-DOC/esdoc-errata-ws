#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
    log "ERRATA-TESTS : running ..."

    nosetests -v -s $ERRATA_HOME/tests

    log "ERRATA-TESTS : complete ..."
}

# Invoke entry point.
main
