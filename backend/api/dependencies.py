from typing import Generator

from api.repositories.event_types_repository import EventTypesRepository
from api.repositories.events_repository import EventsRepository
from api.repositories.medical_records_repository import \
    MedicalRecordsRepository
from api.services.events_extraction_service import (
    BamlEventsExtractionService, EventsExtractionService)
from api.services.text_extraction_service import (TextExtractionService,
                                                  get_text_extraction_service)
from db.session_creator import get_db_session
from fastapi import Depends
from sqlalchemy.orm import Session
from utils.settings import AppSettings
from utils.storage import MinioClient

settings = AppSettings()


def get_storage():
    return MinioClient.from_env(settings=settings)


def get_db() -> Generator[Session, None, None]:
    db = get_db_session(pool_size=10)
    try:
        yield db
    finally:
        db.close()


def get_events_extraction_service(
    session: Session = Depends(get_db),
) -> EventsExtractionService:
    return BamlEventsExtractionService(session=session)


def get_medical_records_repository(
    text_extraction_service: TextExtractionService = Depends(
        get_text_extraction_service
    ),
    events_extraction_service: EventsExtractionService = Depends(
        get_events_extraction_service
    ),
    storage: MinioClient = Depends(get_storage),
    session: Session = Depends(get_db),
) -> MedicalRecordsRepository:
    return MedicalRecordsRepository(
        text_extraction_service=text_extraction_service,
        events_extraction_service=events_extraction_service,
        storage=storage,
        session=session,
    )


def get_event_types_repository(
    session: Session = Depends(get_db),
) -> EventTypesRepository:
    return EventTypesRepository(session=session)


def get_events_repository(session: Session = Depends(get_db)) -> EventsRepository:
    return EventsRepository(session=session)
