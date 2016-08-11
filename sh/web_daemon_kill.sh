#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
	supervisorctl -c $ERRATA_HOME/ops/supervisord.conf stop all
	supervisorctl -c $ERRATA_HOME/ops/supervisord.conf shutdown

	log "WEB : killed web-service daemon"
}

# Invoke entry point.
main
