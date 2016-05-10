#!/bin/bash

# Import utils.
source $ERRATA_HOME/sh/utils.sh

# Main entry point.
main()
{
	log "DB : resetting ..."
	source $ERRATA_DIR_BASH/db_uninstall.sh
	source $ERRATA_DIR_BASH/db_install.sh
	log "DB : reset"
}

# Invoke entry point.
main
