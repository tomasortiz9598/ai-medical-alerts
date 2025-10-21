from collections.abc import Generator
from datetime import date

import pytest
from api.dependencies import (get_db, get_events_extraction_service,
                              get_storage, get_text_extraction_service)
from api.main import app
from api.services.baml_client.types import AlertType, MedicalAlert
from api.services.events_extraction_service import EventsExtractionService
from db.models.base import Base
from db.models.event_type import EventType
from db.session_creator import get_db_session
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

DEFAULT_EVENT_TYPES: tuple[tuple[str, str, str, bool], ...] = (
    (
        "vaccine_expirations",
        "VACCINE_EXPIRATIONS",
        "Vaccine expirations including seasonal boosters",
        False,
    ),
    (
        "upcoming_dental_procedures",
        "UPCOMING_DENTAL_PROCEDURES",
        "Upcoming dental procedures",
        False,
    ),
    (
        "routine_exams",
        "ROUTINE_EXAMS",
        "Routine exams",
        False,
    ),
    (
        "follow_up_appointments",
        "FOLLOW_UP_APPOINTMENTS",
        "Follow-up appointments",
        False,
    ),
)


def _seed_default_event_types(session: Session) -> None:
    existing_ids = {row[0] for row in session.execute(select(EventType.id)).all()}
    to_create = [
        EventType(
            id=identifier,
            name=name,
            description=description,
            is_deletable=is_deletable,
        )
        for identifier, name, description, is_deletable in DEFAULT_EVENT_TYPES
        if identifier not in existing_ids
    ]
    if to_create:
        session.add_all(to_create)
        session.commit()


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    session = get_db_session(create_metadata=True, pool_size=None)
    try:
        Base.metadata.drop_all(bind=session.bind)
        Base.metadata.create_all(bind=session.bind)
        _seed_default_event_types(session)
        yield session
    finally:
        session.rollback()
        session.close()


class StubEventsExtractionService(EventsExtractionService):
    def __init__(self) -> None:
        super().__init__(session=None)

    def extract_events(
        self, text: str, event_types: list[EventType]
    ) -> list[MedicalAlert]:
        return [
            MedicalAlert(
                type=AlertType(
                    id="vaccine_expirations",
                    name="VACCINE_EXPIRATIONS",
                    description="Vaccine expirations including seasonal boosters",
                ),
                event="test",
                date=date.today().isoformat(),
            )
        ]


class StubStorage:
    def put_file(
        self, key: str, data: bytes, content_type: str = "application/octet-stream"
    ) -> None:
        return None


class StubTextExtractionService:
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        return "sample text"


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def _override_db() -> Generator[Session, None, None]:
        yield db_session

    dependency_overrides = {
        get_storage: lambda: StubStorage(),
        get_events_extraction_service: lambda: StubEventsExtractionService(),
        get_text_extraction_service: lambda: StubTextExtractionService(),
        get_db: _override_db,
    }

    app.dependency_overrides.update(dependency_overrides)
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        test_client.close()
        for dependency in dependency_overrides:
            app.dependency_overrides.pop(dependency, None)
