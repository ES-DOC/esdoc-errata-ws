#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

_update_config()
{
	# Create backups.
	cp $ERRATA_WS_HOME/ops/config/supervisord.conf $ERRATA_WS_HOME/ops/config/supervisord-backup.conf
	cp $ERRATA_WS_HOME/ops/config/ws.conf $ERRATA_WS_HOME/ops/config/ws-backup.conf

	# Update.
	cp $ERRATA_WS_HOME/resources/*.conf $ERRATA_WS_HOME/ops/config
}

_update_src()
{
	git pull
}

_update_venv()
{
    pipenv install -r $ESDOC_WS_HOME/requirements.txt
}

# Main entry point.
main()
{
    log "update starts ..."

    pushd $ESDOC_WS_HOME
	_update_src
	_update_config
	_update_venv
	popd
	
    log "update complete"
}

# Invoke entry point.
main
