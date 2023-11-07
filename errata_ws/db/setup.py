from sqlalchemy.schema import CreateSchema
from sqlalchemy.schema import DropSchema

from errata_ws.db import session as db_session
from errata_ws.db.utils import METADATA



# Set of db schemas.
_SCHEMAS = {'errata'}


def execute():
    """Sets up a database.

    """
    # Initialize schemas.
    # db_session.sa_engine.execute(DropSchema('public'))
    for schema in _SCHEMAS:
        try:
            db_session.sa_engine.execute(CreateSchema(schema))
        except:
            pass

    # Initialize tables.
    METADATA.create_all(db_session.sa_engine)
