#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "SECURITY : access control check ..."

    pushd $ERRATA_WS_HOME
	pipenv run python $ERRATA_WS_HOME/sh/check_access_control.py --user=$1 --access-token=$ERRATA_GITHUB_ACCESS_TOKEN --team=$2
    popd
    
    log "SECURITY : access control check complete ..."
}

# Invoke entry point.
main $1 $2
