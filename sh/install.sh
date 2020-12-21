#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

_install_config()
{
	cp $ERRATA_WS_HOME/resources/*.conf $ERRATA_WS_HOME/ops/config
}

_install_ops_dir()
{
	mkdir -p $ERRATA_WS_HOME/ops
	mkdir -p $ERRATA_WS_HOME/ops/config
	mkdir -p $ERRATA_WS_HOME/ops/daemon
	mkdir -p $ERRATA_WS_HOME/ops/logs
	log "ops directory installed"
}

_install_venv()
{
    log "installing virtual environment ..."

	pushd $ERRATA_WS_HOME

    # Update pip / pipenv to latest versions.
    pip2 install --upgrade pip
    pip2 install --upgrade pipenv

	# Install venv using pip env.
	pushd $ERRATA_WS_HOME
	pipenv install

	log "virtual environment installed"
}

# Main entry point.
main()
{
    log "install starts ..."

	_install_ops_dir
	_install_config
	_install_venv

    log "install complete"
}

# Invoke entry point.
main
