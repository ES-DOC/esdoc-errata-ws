# -*- coding: utf-8 -*-

"""
.. module:: prodiguer.db.setup.py
   :platform: Unix
   :synopsis: Initializes database.

.. moduleauthor:: Mark Conway-Greenslade <momipsl@ipsl.jussieu.fr>


"""
from sqlalchemy.schema import CreateSchema
from sqlalchemy.schema import DropSchema

from errata.db import session as db_session
from errata.db.utils import METADATA



# Set of db schemas.
_SCHEMAS = {'errata'}


def execute():
    """Sets up a database.

    """
    # Initialize schemas.
    db_session.sa_engine.execute(DropSchema('public'))
    for schema in _SCHEMAS:
        db_session.sa_engine.execute(CreateSchema(schema))

    # Initialize tables.
    METADATA.create_all(db_session.sa_engine)
