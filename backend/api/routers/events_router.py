from datetime import date
from uuid import UUID

from api.dependencies import get_events_repository
from api.repositories.events_repository import EventsRepository
from api.schemas import EventsResponse
from fastapi import APIRouter, Depends, Query

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=EventsResponse)
async def get_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    event_type_ids: list[str] | None = Query(default=None),
    medical_record_ids: list[str] | None = Query(default=None),
    start_date: date | None = None,
    end_date: date | None = None,
    events_repository: EventsRepository = Depends(get_events_repository),
) -> EventsResponse:
    events, total = events_repository.get_events(
        page=page,
        page_size=page_size,
        event_type_ids=event_type_ids,
        medical_record_ids=[UUID(m_id) for m_id in medical_record_ids]
        if medical_record_ids
        else None,
        start_date=start_date,
        end_date=end_date,
    )
    return EventsResponse(
        events=events,
        total=total,
        page=page,
        page_size=page_size,
    )
