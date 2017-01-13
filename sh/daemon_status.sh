#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
	supervisorctl -c $ERRATA_WS_HOME/ops/config/supervisord.conf status all
}

# Invoke entry point.
main
