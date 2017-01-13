#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
	export PYTHONPATH=$PYTHONPATH:$ERRATA_WS_HOME
	source $ERRATA_WS_HOME/ops/venv/bin/activate
}

# Invoke entry point.
main
