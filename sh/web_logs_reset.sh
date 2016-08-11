#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
	rm $ERRATA_HOME/ops/*.log

	log "WEB : reset web-service logs"
}

# Invoke entry point.
main
