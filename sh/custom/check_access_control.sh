#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "SECURITY : checking access control ..."
    source $ERRATA_WS_HOME/venv/bin/activate
	python $ERRATA_WS_HOME/sh/custom/check_access_control.py --oauth-token=$ERRATA_GITHUB_ACCESS_TOKEN --team=$1
}

# Invoke entry point.
main $1
