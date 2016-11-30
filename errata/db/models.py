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
from errata.utils.constants import FACET_TYPE_DATASET
from errata.utils.constants import FACET_TYPE_EXPERIMENT
from errata.utils.constants import FACET_TYPE_MODEL
from errata.utils.constants import FACET_TYPE_VARIABLE
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

# Facet type enumeration.
_FACET_TYPE_ENUM = Enum(
    FACET_TYPE_DATASET,
    FACET_TYPE_EXPERIMENT,
    FACET_TYPE_MODEL,
    FACET_TYPE_VARIABLE,
    schema=_SCHEMA,
    name="FacetTypeEnum"
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
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    created_by = Column(Unicode(511))
    updated_at = Column(DateTime)
    updated_by = Column(Unicode(511))
    closed_at = Column(DateTime)
    closed_by = Column(Unicode(511))
    materials = Column(Text)


    def __repr__(self):
        """Instance representation.

        """
        return "<Issue(id={}, uid={}, title={}, description=={})>".format(
            self.id, self.uid, self.title, self.description)


# Set unique description (case insensitive) index.
Index('idx_issue_description', func.lower(Issue.description))


class IssueFacet(Entity):
    """Associates an issue with a searchable facet such as dataset id.

    """
    # SQLAlchemy directives.
    __tablename__ = 'tbl_issue_facet'
    __table_args__ = (
        UniqueConstraint('issue_uid', 'facet_id', 'facet_type'),
        {'schema': _SCHEMA}
    )

    # Column definitions.
    issue_uid = Column(Unicode(63),
                       ForeignKey('{}.tbl_issue.uid'.format(_SCHEMA)), nullable=False)
    facet_id = Column(Unicode(1023), nullable=False, index=True)
    facet_type = Column(_FACET_TYPE_ENUM, nullable=False)
