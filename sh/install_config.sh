#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
	cp $ERRATA_WS_HOME/resources/supervisord.conf $ERRATA_WS_HOME/ops/config
	cp $ERRATA_WS_HOME/resources/ws.conf $ERRATA_WS_HOME/ops/config
	cp $ERRATA_WS_HOME/resources/projects.json $ERRATA_WS_HOME/ops/config

	log "configuration files initialized"
}

# Invoke entry point.
main
