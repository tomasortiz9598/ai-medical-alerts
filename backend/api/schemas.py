import datetime
import uuid
from datetime import date

from pydantic import BaseModel


class EventTypeBase(BaseModel):
    name: str
    description: str


class EventType(EventTypeBase):
    id: str
    is_deletable: bool


class UpcomingEvent(BaseModel):
    type: EventType
    description: str
    date: date
    medical_record_id: uuid.UUID | None = None
    medical_record_filename: str | None = None


class EventsResponse(BaseModel):
    events: list[UpcomingEvent]
    total: int | None = None
    page: int | None = None
    page_size: int | None = None


class UploadAlert(BaseModel):
    type: str
    event: str
    date: date


class UploadResponse(BaseModel):
    alerts: list[UploadAlert]


class MedicalRecord(BaseModel):
    id: uuid.UUID
    filename: str
    created_time: datetime.datetime


class MedicalRecordResponse(BaseModel):
    medical_records: list[MedicalRecord]
