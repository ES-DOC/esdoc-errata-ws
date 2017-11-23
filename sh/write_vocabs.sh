#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "update starts ..."

    source $ERRATA_WS_HOME/sh/activate_venv.sh
	python $ERRATA_WS_HOME/sh/write_vocabs.py

    log "update complete"
}

# Invoke entry point.
main
