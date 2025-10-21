from api.error_handlers import InvalidRequest
from api.schemas import EventType as EventTypeSchema
from db.models.event import Event
from db.models.event_type import EventType
from sqlalchemy.orm import Session


class EventTypesRepository:
    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def get_event_types(self) -> list[EventTypeSchema]:
        event_types: list[EventType] = self.session.query(EventType).all()
        return [
            EventTypeSchema(
                id=event_type.id,
                name=event_type.name,
                description=event_type.description,
                is_deletable=event_type.is_deletable,
            )
            for event_type in event_types
        ]

    def delete_event_type(self, event_type_id: str) -> None:
        events: list[Event] = (
            self.session.query(Event).filter(Event.event_type_id == event_type_id).all()
        )
        for event in events:
            self.session.delete(event)

        event_type: EventType | None = (
            self.session.query(EventType).filter(EventType.id == event_type_id).first()
        )
        if not event_type:
            raise InvalidRequest(f"Event type {event_type_id} not found")
        if not event_type.is_deletable:
            raise InvalidRequest(f"Event type {event_type.name} is not deletable")
        self.session.delete(event_type)
        self.session.commit()

    def create_event_type(self, name: str, description: str) -> EventTypeSchema:
        event_type = EventType.create(name=name, description=description)
        self.session.add(event_type)
        self.session.commit()
        return EventTypeSchema(
            id=event_type.id,
            name=event_type.name,
            description=event_type.description,
            is_deletable=event_type.is_deletable,
        )
