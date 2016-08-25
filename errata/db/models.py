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

from sqlalchemy import func
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Text
from sqlalchemy import Unicode
from sqlalchemy import UniqueConstraint
from sqlalchemy import Enum


from errata.db.utils import Entity
from errata.utils.constants import STATUS_NEW
from errata.utils.constants import STATUS_ON_HOLD
from errata.utils.constants import STATUS_RESOLVED
from errata.utils.constants import STATUS_WONT_FIX
from errata.utils.constants import SEVERITY_LOW
from errata.utils.constants import SEVERITY_MEDIUM
from errata.utils.constants import SEVERITY_HIGH
from errata.utils.constants import SEVERITY_CRITICAL



# Database schema.
_SCHEMA = 'errata'

# Issue status enumeration.
_STATUS_ENUM = Enum(
    STATUS_NEW,
    STATUS_ON_HOLD,
    STATUS_RESOLVED,
    STATUS_WONT_FIX,
    schema=_SCHEMA,
    name="IssueWorkflowEnum"
    )

# Issue severity enumeration.
_SEVERITY_ENUM = Enum(
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    SEVERITY_HIGH,
    SEVERITY_CRITICAL,
    schema=_SCHEMA,
    name="IssueSeverityEnum"
    )


class Issue(Entity):
    """An issue raised by an institute post-publication.

    """
    # SQLAlchemy directives.
    __tablename__ = 'tbl_issue'
    __table_args__ = (
        {'schema': _SCHEMA}
    )

    # Column definitions.
    project = Column(Unicode(63), nullable=False)
    institute = Column(Unicode(63), nullable=False)
    uid = Column(Unicode(63), nullable=False, unique=True, default=uuid.uuid4())
    title = Column(Unicode(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(_SEVERITY_ENUM, nullable=False)
    status = Column(_STATUS_ENUM, nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    date_updated = Column(DateTime)
    date_closed = Column(DateTime)
    url = Column(Unicode(1023))
    materials = Column(Text)


    def __repr__(self):
        """Instance representation.

        """
        return "<Issue(id={}, uid={}, title={}, description=={})>".format(
            self.id, self.uid, self.title, self.description)


# Set unique description (case insensitive) index.
Index('idx_issue_description', func.lower(Issue.description))


class IssueDataset(Entity):
    """Associates an issue with a dataset.

    """
    # SQLAlchemy directives.
    __tablename__ = 'tbl_issue_dataset'
    __table_args__ = (
        UniqueConstraint('issue_uid', 'dataset_id'),
        {'schema': _SCHEMA}
    )

    # Column definitions.
    issue_uid = Column(Unicode(63),
                       ForeignKey('{}.tbl_issue.uid'.format(_SCHEMA)), nullable=False)
    dataset_id = Column(Unicode(1023), nullable=False, index=True)


class IssueModel(Entity):
    """Associates an issue with a model.

    """
    # SQLAlchemy directives.
    __tablename__ = 'tbl_issue_model'
    __table_args__ = (
        UniqueConstraint('issue_uid', 'model_id'),
        {'schema': _SCHEMA}
    )

    # Column definitions.
    issue_uid = Column(Unicode(63),
                       ForeignKey('{}.tbl_issue.uid'.format(_SCHEMA)), nullable=False)
    model_id = Column(Unicode(63), nullable=False, index=True)
