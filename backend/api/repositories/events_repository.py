from datetime import date
from tracemalloc import start
from uuid import UUID

from api.error_handlers import InvalidRequest
from api.schemas import EventType, UpcomingEvent
from db.models.event import Event
from sqlalchemy.orm import Session


class EventsRepository:
    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def get_events(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        event_type_ids: list[str] | None = None,
        medical_record_ids: list[UUID] | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> tuple[list[UpcomingEvent], int]:
        query = self.session.query(Event)

        if event_type_ids:
            query = query.filter(Event.event_type_id.in_(event_type_ids))
        if medical_record_ids:
            query = query.filter(Event.medical_record_id.in_(medical_record_ids))
        if start_date:
            query = query.filter(Event.date >= start_date)
        else:
            query = query.filter(Event.date >= date.today())
        if end_date:
            query = query.filter(Event.date <= end_date)

        total = query.count()

        page = max(page, 1)
        page_size = max(page_size, 1)

        events: list[Event] = (
            query.order_by(Event.date)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        result: list[UpcomingEvent] = []
        for event in events:
            record = getattr(event, "medical_record", None)
            result.append(
                UpcomingEvent(
                    type=EventType(
                        id=event.type.id,
                        name=event.type.name,
                        description=event.type.description,
                        is_deletable=event.type.is_deletable,
                    ),
                    description=event.event,
                    date=event.date,
                    medical_record_id=event.medical_record_id,
                    medical_record_filename=getattr(record, "filename", None),
                )
            )
        return result, total
