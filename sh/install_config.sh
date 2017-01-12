#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
	cp $ERRATA_WS_HOME/resources/template-supervisord.conf $ERRATA_WS_HOME/ops/config/supervisord.conf
	cp $ERRATA_WS_HOME/resources/template-ws.conf $ERRATA_WS_HOME/ops/config/ws.conf

	log "configuration files initialized"
}

# Invoke entry point.
main
