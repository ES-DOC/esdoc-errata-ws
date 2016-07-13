#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "SH : installing requirements ..."
    /usr/local/bin/python2.7 /usr/bin/pip install -r $ERRATA_HOME/requirements.txt
}

# Invoke entry point.
main
