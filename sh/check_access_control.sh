#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "SECURITY : access control check ..."

    source $ERRATA_WS_HOME/sh/activate_venv.sh
	python $ERRATA_WS_HOME/sh/check_access_control.py --oauth-token=$ERRATA_GITHUB_ACCESS_TOKEN --team=$1

    log "SECURITY : access control check complete ..."
}

# Invoke entry point.
main $1
