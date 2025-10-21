import uuid
from datetime import date as Date
from typing import TYPE_CHECKING

from db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from db.models.event_type import EventType
    from db.models.medical_record import MedicalRecord


class Event(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "events"

    medical_record_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("medical_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_type_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("event_types.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[Date] = mapped_column(nullable=False)

    medical_record: Mapped["MedicalRecord"] = relationship(
        "MedicalRecord",
        back_populates="events",
    )
    type: Mapped["EventType"] = relationship(
        "EventType",
        back_populates="events",
    )
