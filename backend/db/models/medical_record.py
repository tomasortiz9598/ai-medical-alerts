from typing import TYPE_CHECKING

from db.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from db.models.event import Event


class MedicalRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "medical_records"

    filename: Mapped[str] = mapped_column(nullable=False)

    events: Mapped[list["Event"]] = relationship(
        back_populates="medical_record",
        cascade="all, delete-orphan",
    )

    @property
    def storage_uri(self) -> str:
        return f"{self.id}/{self.filename}"
