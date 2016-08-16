#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
	source $ERRATA_HOME/sh/web_logs_reset.sh
	supervisord -c $ERRATA_HOME/ops/supervisord.conf

	log "WEB : initialized web-service daemon"
}

# Invoke entry point.
main
