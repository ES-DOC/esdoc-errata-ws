#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/init.sh

# Main entry point.
main()
{
	log "DB : resetting ..."
	source $ERRATA_HOME/sh/db_uninstall.sh
	source $ERRATA_HOME/sh/db_install.sh
	log "DB : reset"
}

# Invoke entry point.
main
