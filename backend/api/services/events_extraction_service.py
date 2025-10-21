import traceback
from abc import ABC, abstractmethod

from api.error_handlers import InvalidRequest
from api.services.baml_client import b
from api.services.baml_client.types import AlertType, MedicalAlert
from db.models.event_type import EventType
from sqlalchemy.orm import Session


class EventsExtractionService(ABC):
    def __init__(self, session: Session):
        self.session = session

    @abstractmethod
    def extract_events(
        self, text: str, event_types: list[EventType]
    ) -> list[MedicalAlert]:
        raise NotImplementedError


class BamlEventsExtractionService(EventsExtractionService):
    def __init__(self, session: Session):
        super().__init__(session)

    def extract_events(
        self, text: str, event_types: list[EventType]
    ) -> list[MedicalAlert]:
        alert_types = [
            AlertType(
                id=alert_type.id,
                name=alert_type.name,
                description=alert_type.description,
            )
            for alert_type in event_types
        ]
        try:
            return b.ExtractMedicalAlerts(document=text, alert_types=alert_types)
        except Exception as exc:
            traceback.print_exc()
            raise InvalidRequest(
                "Unable to extract medical alerts from the uploaded document. Please try again shortly."
            ) from exc
