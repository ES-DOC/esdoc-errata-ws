#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
	rm $ERRATA_WS_HOME/ops/logs/*.log

	log "logs reset"
}

# Invoke entry point.
main
