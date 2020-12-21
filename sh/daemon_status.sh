#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
	pushd $ERRATA_WS_HOME
	supervisorctl -c $ERRATA_WS_HOME/ops/config/supervisord.conf status all
	popd
}

# Invoke entry point.
main
