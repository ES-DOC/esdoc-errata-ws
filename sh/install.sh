#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "install starts ..."

	source $ERRATA_WS_HOME/sh/install_config.sh
	source $ERRATA_WS_HOME/sh/install_venv.sh

    log "install complete"
}

# Invoke entry point.
main