from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UUIDPrimaryKeyMixin:
    # For PostgreSQL: PG_UUID(as_uuid=True)
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),  # TODO: swap to String(36) for SQLite if needed
        primary_key=True,
        default=uuid.uuid4,  # generated in Python (portable & simple)
    )


class TimestampMixin:
    # timezone-aware timestamps
    created_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # DB-side default
        nullable=False,
    )
    updated_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # initial value
        onupdate=func.now(),  # auto-update on UPDATE
        nullable=False,
    )
