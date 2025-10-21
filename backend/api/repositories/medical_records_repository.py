import uuid
from datetime import datetime

from api.error_handlers import InvalidRequest
from api.schemas import EventType as EventTypeSchema
from api.schemas import MedicalRecord as MedicalRecordSchema
from api.schemas import UpcomingEvent
from api.services.events_extraction_service import EventsExtractionService
from api.services.text_extraction_service import TextExtractionService
from db.models.event import Event
from db.models.event_type import EventType
from db.models.medical_record import MedicalRecord
from sqlalchemy.orm import Session
from utils.storage import MinioClient


class MedicalRecordsRepository:
    def __init__(
        self,
        text_extraction_service: TextExtractionService,
        events_extraction_service: EventsExtractionService,
        storage: MinioClient,
        session: Session,
    ):
        self.text_extraction_service = text_extraction_service
        self.events_extraction_service = events_extraction_service
        self.storage = storage
        self.session = session

    def delete_medical_record(self, medical_record_id: uuid.UUID) -> None:
        medical_record: MedicalRecord | None = (
            self.session.query(MedicalRecord)
            .filter(MedicalRecord.id == medical_record_id)
            .one_or_none()
        )
        if not medical_record:
            raise InvalidRequest(f"Medical record {medical_record_id} not found")
        self.session.delete(medical_record)
        self.session.commit()

    def process_medical_record(self, blob: bytes, filename: str) -> list[UpcomingEvent]:
        medical_record_id = uuid.uuid4()
        medical_record = MedicalRecord(id=medical_record_id, filename=filename)
        self.session.add(medical_record)

        text = self.text_extraction_service.extract_text_from_pdf(blob)

        event_types: list[EventType] = self.session.query(EventType).all()
        medical_events = self.events_extraction_service.extract_events(
            text=text, event_types=event_types
        )

        upcoming_events = []
        for medical_event in medical_events:
            event_date = datetime.fromisoformat(medical_event.date).date()
            self.session.add(
                Event(
                    medical_record_id=medical_record_id,
                    event_type_id=medical_event.type.id,
                    event=medical_event.event,
                    date=event_date,
                )
            )
            upcoming_events.append(
                UpcomingEvent(
                    type=EventTypeSchema(
                        id=medical_event.type.id,
                        name=medical_event.type.name,
                        description=medical_event.type.description,
                        is_deletable=False,
                    ),
                    description=medical_event.event,
                    date=event_date,
                )
            )

        self.session.commit()
        self.storage.put_file(key=medical_record.storage_uri, data=blob)

        return sorted(upcoming_events, key=lambda x: x.date, reverse=True)

    def get_medical_records(self) -> list[MedicalRecordSchema]:
        medical_records: list[MedicalRecord] = (
            self.session.query(MedicalRecord)
            .order_by(MedicalRecord.created_time.desc())
            .all()
        )
        return [
            MedicalRecordSchema(
                id=medical_record.id,
                filename=medical_record.filename,
                created_time=medical_record.created_time,
            )
            for medical_record in medical_records
        ]
