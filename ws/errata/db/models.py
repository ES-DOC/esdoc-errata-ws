# -*- coding: utf-8 -*-
"""
.. module:: db.models.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - db tables.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import datetime
import uuid

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import Unicode
from sqlalchemy import UniqueConstraint
from sqlalchemy import Enum

from errata.db.utils import Entity

# Database schema.
_SCHEMA = 'errata'


class Issue(Entity):
    """An issue raised by an institute post-publication.

    """
    # SQLAlchemy directives.
    __tablename__ = 'tbl_issue'
    __table_args__ = (
        {'schema':_SCHEMA}
    )

    # TODO define columns
    uid = Column(Unicode(255), nullable=False, unique=True, default=uuid.uuid4())
    # status = Column(Unicode(31), nullable=False)
    title = Column(Unicode(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum('Open', 'Closed'), nullable=False)
    state = Column(Enum('New', 'On Hold', 'Wont Fix', 'Resolved', name='State'))
    severity = Column(Enum('Low', 'Medium', 'High', 'Critical', name='Severity'))
    issue_created_date = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    issue_updated_date = Column(DateTime)
    issue_closed_date = Column(DateTime)
    url = Column(Unicode(255))
    materials = Column(Text)
    dsets = Column(Text)

    # NOTE: following columns already defined upon base class:
    #       id, row_create_date, row_update_date
    # E.G. https://github.com/ES-DOC/esdoc-api/esdoc_api/db/models/docs.py
