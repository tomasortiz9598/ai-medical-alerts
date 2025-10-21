from api.dependencies import get_event_types_repository
from api.repositories.event_types_repository import EventTypesRepository
from api.schemas import EventType, EventTypeBase
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/event-types", tags=["event_types"])


@router.get("", response_model=list[EventType])
async def get_event_types(
    event_types_repository: EventTypesRepository = Depends(get_event_types_repository),
) -> list[EventType]:
    return event_types_repository.get_event_types()


@router.post("", response_model=EventType, status_code=201)
async def create_event_type(
    event_type: EventTypeBase,
    event_types_repository: EventTypesRepository = Depends(get_event_types_repository),
) -> EventType:
    return event_types_repository.create_event_type(
        name=event_type.name, description=event_type.description
    )


@router.delete("/{event_type_id}", status_code=204)
async def delete_event_type(
    event_type_id: str,
    event_types_repository: EventTypesRepository = Depends(get_event_types_repository),
) -> None:
    event_types_repository.delete_event_type(event_type_id=event_type_id)
