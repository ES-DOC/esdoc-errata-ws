#!/bin/bash

# Import utils.
source $ERRATA_WS_HOME/sh/utils.sh

# Main entry point.
main()
{
    log "ERRATA-TESTS : execution starts ..."

    source $ERRATA_WS_HOME/sh/activate_venv.sh
    # nosetests -v -s $ERRATA_WS_HOME/tests
    # nosetests -v -s $ERRATA_WS_HOME/tests/test_config.py
    # nosetests -v -s $ERRATA_WS_HOME/tests/test_config_esg.py
    # nosetests -v -s $ERRATA_WS_HOME/tests/test_ops.py
    nosetests -v -s $ERRATA_WS_HOME/tests/test_search.py
    nosetests -v -s $ERRATA_WS_HOME/tests/test_publishing.py

    log "ERRATA-TESTS : execution complete ..."
}

# Invoke entry point.
main
