# -*- coding: utf-8 -*-

"""
.. module:: run_db_setup.py
   :license: GPL/CeCIL
   :platform: Unix, Windows
   :synopsis: Sets up errata db tables for use.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
from errata import db
from errata.utils import config
from errata.utils import logger



# Name of standard db user.
_DB_USER = "esdoc_errata_db_user"

# Name of admin db user.
_DB_ADMIN_USER = "esdoc_errata_db_admin"


def _main():
    """Main entry point.

    """
    # Db connection must be admin.
    connection = config.db.replace(_DB_USER, _DB_ADMIN_USER)

    logger.log_db("db setup begins : db = {0}".format(connection))

    # Run setup in context of a session.
    with db.session.create(connection):
        db.setup.execute()

    logger.log_db("db setup ends : db = {0}".format(connection))



if __name__ == '__main__':
    _main()
