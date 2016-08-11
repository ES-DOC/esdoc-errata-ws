#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
	cp $ERRATA_HOME/templates/template-supervisord.conf $ERRATA_HOME/ops/supervisord.conf
	cp $ERRATA_HOME/templates/template-ws.conf $ERRATA_HOME/ops/ws.conf

	log "WEB : initialized web-service configuation"
}

# Invoke entry point.
main
