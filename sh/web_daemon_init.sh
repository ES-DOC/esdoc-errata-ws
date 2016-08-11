#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
	source $ERRATA_HOME/sh/web_daemons_reset_logs.sh
	supervisord -c $ERRATA_HOME/ops/supervisord.conf

	log "WEB : initialized web-service daemon"
}

# Invoke entry point.
main
