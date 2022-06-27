# -*- coding: utf-8 -*-

"""
.. module:: run_db_setup.py
   :license: GPL/CeCIL
   :platform: Unix, Windows
   :synopsis: Sets up errata db tables for use.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import os

from errata import db
from errata.utils import config
from errata.utils import logger



def _main():
    """Main entry point.

    """
    logger.log_db("db setup begins : db = {0}".format(config.db))

    db_connection = config.db
    if os.getenv("ERRATA_DB_PWD"):
        db_connection = db_connection.replace("ENV_ERRATA_DB_PWD", os.getenv("ERRATA_DB_PWD"))

    with db.session.create(db_connection):
        db.setup.execute()

    logger.log_db("db setup ends : db = {0}".format(config.db))


if __name__ == '__main__':
    _main()
