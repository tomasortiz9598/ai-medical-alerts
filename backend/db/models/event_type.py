from typing import TYPE_CHECKING

from db.models.base import Base, TimestampMixin
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from db.models.event import Event


class EventType(TimestampMixin, Base):
    __tablename__ = "event_types"

    id: Mapped[str] = mapped_column(nullable=False, primary_key=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)

    is_deletable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    description: Mapped[str] = mapped_column(String(255), nullable=False)

    events: Mapped[list["Event"]] = relationship("Event", back_populates="type")

    @classmethod
    def create(
        cls, name: str, description: str, is_deletable: bool = True
    ) -> "EventType":
        return cls(
            id=name.lower().replace(" ", "_"),
            name=name,
            description=description,
            is_deletable=is_deletable,
        )
