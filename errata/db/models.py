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
from errata.utils import config
from errata.utils import convertor
from errata.utils.constants import *


# Database schema.
_SCHEMA = 'errata'

# Issue status enumeration.
_ISSUE_MODERATION_ENUM = Enum(
    ISSUE_MODERATION_ACCEPTED,
    ISSUE_MODERATION_IN_REVIEW,
    ISSUE_MODERATION_NOT_REQUIRED,
    ISSUE_MODERATION_REJECTED,
    schema=_SCHEMA,
    name="IssueModerationEnum"
    )

# Issue status enumeration.
_ISSUE_STATUS_ENUM = Enum(
    ISSUE_STATUS_NEW,
    ISSUE_STATUS_ON_HOLD,
    ISSUE_STATUS_RESOLVED,
    ISSUE_STATUS_WONT_FIX,
    schema=_SCHEMA,
    name="IssueWorkflowEnum"
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

# Issue resource type enumeration.
_ISSUE_RESOURCE_ENUM = Enum(
    ISSUE_RESOURCE_URL,
    ISSUE_RESOURCE_MATERIAL,
    ISSUE_RESOURCE_DATASET,
    schema=_SCHEMA,
    name="IssueResourceTypeEnum"
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

    # Core columns.
    project = Column(Unicode(63), nullable=False)
    institute = Column(Unicode(63), nullable=False)
    uid = Column(Unicode(63), nullable=False, unique=True, default=uuid.uuid4())
    title = Column(Unicode(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(_ISSUE_SEVERITY_ENUM, nullable=False)
    status = Column(_ISSUE_STATUS_ENUM, nullable=False)
    moderation_status = Column(
        _ISSUE_MODERATION_ENUM,
        nullable=False,
        default=ISSUE_MODERATION_NOT_REQUIRED
        )
    moderation_window = Column(
        DateTime,
        nullable=False,
        default=lambda: (dt.datetime.utcnow() + dt.timedelta(days=config.moderation.window_in_days))
        )

    # Tracking columns.
    created_by = Column(Unicode(511))
    created_by_email = Column(Unicode(511), nullable=True)
    created_date = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_by = Column(Unicode(511))
    updated_date = Column(DateTime)
    closed_by = Column(Unicode(511))
    closed_date = Column(DateTime)


    def __repr__(self):
        """Instance representation.

        """
        return "<Issue(uid={}, title={}, description=={})>".format(
            self.uid, self.title, self.description)


    def to_dict(self, resources, facets):
        """Encode object as a simple dictionary.

        :param list resources: Collection of issue resources.
        :param list facets: Collection of issue facets.

        """
        def _get_facets():
            return sorted(['{}:{}'.format(i.facet_type, i.facet_value) for i in facets if i.issue_uid == self.uid])

        def _get_reources(resource_type):
            return sorted([i.resource_location for i in resources \
                           if i.issue_uid == self.uid and i.resource_type == resource_type])

        obj = convertor.to_dict(self)
        obj['facets'] = _get_facets()
        obj['datasets'] = _get_reources(ISSUE_RESOURCE_DATASET)
        obj['materials'] = _get_reources(ISSUE_RESOURCE_MATERIAL)
        obj['urls'] = _get_reources(ISSUE_RESOURCE_URL)

        return obj


# Set unique description (case insensitive) index.
Index('idx_issue_description', func.lower(Issue.description))


class IssueFacet(Entity):
    """Associates an issue with a searchable facet such as severity.

    """
    # SQLAlchemy directives.
    __tablename__ = 'tbl_issue_facet'
    __table_args__ = (
        UniqueConstraint('issue_uid', 'facet_value', 'facet_type'),
        {'schema': _SCHEMA}
    )

    # Column definitions.
    project = Column(Unicode(63), nullable=False)
    issue_uid = Column(Unicode(63), ForeignKey('{}.tbl_issue.uid'.format(_SCHEMA)), nullable=False)
    facet_type = Column(Unicode(63), nullable=False)
    facet_value = Column(Unicode(1023), nullable=False, index=True)


    def __repr__(self):
        """Instance representation.

        """
        return "<IssueFacet(uid={}, type={}, value=={})>".format(
            self.issue_uid, self.facet_type, self.facet_value)


class IssueResource(Entity):
    """Associates an issue with a resource such as a dataset id.

    """
    # SQLAlchemy directives.
    __tablename__ = 'tbl_issue_resource'
    __table_args__ = (
        UniqueConstraint('issue_uid', 'resource_type', 'resource_location'),
        {'schema': _SCHEMA}
    )

    # Column definitions.
    issue_uid = Column(Unicode(63), ForeignKey('{}.tbl_issue.uid'.format(_SCHEMA)), nullable=False)
    resource_type = Column(_ISSUE_RESOURCE_ENUM, nullable=False)
    resource_location = Column(Unicode(1023), nullable=False)


    def __repr__(self):
        """Instance representation.

        """
        return "<IssueResource(uid={}, type={}, location=={})>".format(
            self.issue_uid, self.resource_type, self.resource_location)


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


    def __repr__(self):
        """Instance representation.

        """
        return "<PIDServiceTask(uid={}, dataset_id={}, action={}, status=={})>".format(
            self.issue_uid, self.dataset_id, self.action, self.status)


    def to_dict(self):
        """Encode object as a simple dictionary.

        """
        return convertor.to_dict(self)

