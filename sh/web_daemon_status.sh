#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
	supervisorctl -c $ERRATA_HOME/ops/supervisord.conf status all
}

# Invoke entry point.
main
