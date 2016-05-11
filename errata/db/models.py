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
from errata.constants import ISSUE_STATE_NEW
from errata.constants import ISSUE_STATE_ON_HOLD
from errata.constants import ISSUE_STATE_RESOLVED
from errata.constants import ISSUE_STATE_WONT_FIX
from errata.constants import ISSUE_STATUS_OPEN
from errata.constants import ISSUE_STATUS_CLOSED
from errata.constants import ISSUE_SEVERITY_LOW
from errata.constants import ISSUE_SEVERITY_MEDIUM
from errata.constants import ISSUE_SEVERITY_HIGH
from errata.constants import ISSUE_SEVERITY_CRITICAL


# Database schema.
_SCHEMA = 'errata'



# Issue type enumeration.
_ISSUE_STATE_ENUM = Enum(
    ISSUE_STATE_NEW,
    ISSUE_STATE_ON_HOLD,
    ISSUE_STATE_RESOLVED,
    ISSUE_STATE_WONT_FIX,
    schema=_SCHEMA,
    name="IssueStateEnum"
    )

# Issue type enumeration.
_ISSUE_STATUS_ENUM = Enum(
    ISSUE_STATUS_OPEN,
    ISSUE_STATUS_CLOSED,
    schema=_SCHEMA,
    name="IssueStatusEnum"
    )

# Issue severity enumeration.
_ISSUE_SEVERITY_ENUM = Enum(
    ISSUE_SEVERITY_LOW,
    ISSUE_SEVERITY_MEDIUM,
    ISSUE_SEVERITY_HIGH,
    ISSUE_SEVERITY_CRITICAL,
    schema=_SCHEMA,
    name="IssueSeverityEnum"
    )


class Issue(Entity):
    """An issue raised by an institute post-publication.

    """
    # SQLAlchemy directives.
    __tablename__ = 'tbl_issue'
    __table_args__ = (
        {'schema':_SCHEMA}
    )

    uid = Column(Unicode(255), nullable=False, unique=True, default=uuid.uuid4())
    title = Column(Unicode(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(_ISSUE_STATUS_ENUM, nullable=False)
    state = Column(_ISSUE_STATE_ENUM, nullable=False)
    severity = Column(_ISSUE_SEVERITY_ENUM, nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    date_updated = Column(DateTime)
    date_closed = Column(DateTime)
    url = Column(Unicode(1023))
    materials = Column(Text)
    dsets = Column(Text)

    # NOTE: following columns already defined upon base class:
    #       id, row_create_date, row_update_date
    # E.G. https://github.com/ES-DOC/esdoc-api/esdoc_api/db/models/docs.py
