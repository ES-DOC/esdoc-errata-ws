# -*- coding: utf-8 -*-
"""
.. module:: db.models.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - db tables.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import collections
import datetime as dt
import uuid

from sqlalchemy import func
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import Unicode
from sqlalchemy import UniqueConstraint
from sqlalchemy import Enum

from errata.db.utils import Entity
from errata.utils import convertor
from errata.utils.constants import *



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

# PID task states.
_PID_TASK_STATE_ENUM = Enum(
    PID_TASK_STATE_COMPLETE,
    PID_TASK_STATE_ERROR,
    PID_TASK_STATE_QUEUED,
    schema=_SCHEMA,
    name="PIDTaskStateEnum"
    )


# PID action types.
_PID_ACTION_ENUM = Enum(
    PID_ACTION_INSERT,
    PID_ACTION_DELETE,
    schema=_SCHEMA,
    name="PIDActionEnum"
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
    url = Column(Unicode(1023))
    date_created = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    date_updated = Column(DateTime)
    date_closed = Column(DateTime)
    created_by = Column(Unicode(511))
    updated_by = Column(Unicode(511))
    closed_by = Column(Unicode(511))
    materials = Column(Text)


    def __repr__(self):
        """Instance representation.

        """
        return "<Issue(id={}, uid={}, title={}, description=={})>".format(
            self.id, self.uid, self.title, self.description)


    def to_dict(self, facets):
        """Encode issue as a simple dictionary.

        """
        obj = convertor.to_dict(self)
        obj['materials'] = sorted(self.materials.split(","))
        obj['datasets'] = []
        obj['facets'] = collections.defaultdict(list)
        for facet_value, facet_type, _ in [i for i in facets if i[2] == self.uid]:
            if facet_type == 'dataset':
                obj['datasets'].append(facet_value)
            elif facet_type not in CORE_FACET_TYPES:
                obj['facets'][facet_type].append(facet_value)

        return obj


# Set unique description (case insensitive) index.
Index('idx_issue_description', func.lower(Issue.description))


class IssueFacet(Entity):
    """Associates an issue with a searchable facet such as dataset id.

    """
    # SQLAlchemy directives.
    __tablename__ = 'tbl_issue_facet'
    __table_args__ = (
        UniqueConstraint('issue_uid', 'facet_value', 'facet_type'),
        {'schema': _SCHEMA}
    )

    # Column definitions.
    issue_uid = Column(Unicode(63), ForeignKey('{}.tbl_issue.uid'.format(_SCHEMA)), nullable=False)
    facet_value = Column(Unicode(1023), nullable=False, index=True)
    facet_type = Column(Unicode(63), nullable=False)


class PIDServiceTask(Entity):
    """Tasks to be dispatched to PID handler service.

    """
    # SQLAlchemy directives.
    __tablename__ = 'tbl_pid_service_task'
    __table_args__ = (
        {'schema': _SCHEMA}
    )

    # Column definitions.
    action = Column(_PID_ACTION_ENUM, nullable=False)
    status = Column(_PID_TASK_STATE_ENUM, nullable=False, default=PID_TASK_STATE_QUEUED)
    issue_uid = Column(Unicode(63), ForeignKey('{}.tbl_issue.uid'.format(_SCHEMA)), nullable=False)
    dataset_id = Column(Unicode(1023), nullable=False)
    error = Column(Unicode(1023))
    try_count = Column(Integer, default=0)
    timestamp = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
