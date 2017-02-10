#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
	source $ERRATA_WS_HOME/sh/daemon_stop.sh
	source $ERRATA_WS_HOME/sh/daemon_start.sh
	sleep 3.0
	source $ERRATA_WS_HOME/sh/daemon_status.sh
}

# Invoke entry point.
main
