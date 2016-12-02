#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
    log "SECURITY : checking access control ..."
    source $ERRATA_HOME/venv/bin/activate
	python $ERRATA_HOME/sh/check_access_control.py --oauth-token=$ERRATA_GITHUB_ACCESS_TOKEN --team=$1
}

# Invoke entry point.
main $1
