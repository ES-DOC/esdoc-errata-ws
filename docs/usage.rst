============================
ES-DOC Errata Usage Guide
============================

Upon successful `installation <https://github.com/ES-DOC/esdoc-errata-ws/blob/master/docs/installation.rst>`_ of the errata web-service the following commands can invoked from the command line:  

errata-db-install
----------------------------

Installs errata PostgreSQL database.

errata-db-reset
----------------------------

Uninstalls and reinstalls errata PostgreSQL database.  Used during development when database schema changes.

errata-db-uninstall
----------------------------

Drops errata PostgreSQL database.  Called during development as part of a database reset.

errata-db-insert-test-issues [INPUT-DIR]
----------------------------

Inserts tests issues into database from all JSON files within input directory.

**INPUT-DIR**

	Directory within which are issue JSON files.  Defaults to contents of `test-data <https://github.com/ES-DOC/esdoc-errata/tree/master/test-data>`_.

errata-venv-setup
----------------------------

Installs required python dependencies.

errata-ws
----------------------------

Launches the errata web service in interactive mode.
