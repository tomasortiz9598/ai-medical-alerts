from datetime import date, timedelta
from uuid import UUID, uuid4

import pytest
from db.models.event import Event
from db.models.event_type import EventType
from db.models.medical_record import MedicalRecord
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

FUTURE_BASE_DATE = date.today() + timedelta(days=1)


def _create_medical_record(
    session: Session, filename: str = "record.pdf"
) -> MedicalRecord:
    record = MedicalRecord(id=uuid4(), filename=filename)
    session.add(record)
    session.flush()
    return record


def _ensure_event_type(session: Session, identifier: str, name: str) -> EventType:
    event_type = session.query(EventType).filter(EventType.id == identifier).first()
    if event_type:
        return event_type
    event_type = EventType(
        id=identifier,
        name=name,
        description=f"Description for {name}",
        is_deletable=True,
    )
    session.add(event_type)
    session.commit()
    return event_type


def _add_event(
    session: Session,
    *,
    event_type_id: str,
    event_date: date,
    description: str,
    medical_record_id: UUID | None = None,
) -> UUID:
    if medical_record_id is None:
        record = _create_medical_record(session)
        medical_record_id = record.id
    event = Event(
        id=uuid4(),
        medical_record_id=medical_record_id,
        event_type_id=event_type_id,
        event=description,
        date=event_date,
    )
    session.add(event)
    session.commit()
    return medical_record_id


@pytest.fixture
def seeded_events(db_session: Session):
    custom_type = _ensure_event_type(db_session, "custom_type", "CUSTOM_TYPE")
    follow_type = _ensure_event_type(db_session, "follow_type", "FOLLOW_TYPE")

    record_a = _create_medical_record(db_session, "record_a.pdf")
    record_b = _create_medical_record(db_session, "record_b.pdf")
    record_c = _create_medical_record(db_session, "record_c.pdf")

    base_date = FUTURE_BASE_DATE
    events_payload = [
        {
            "event_type_id": custom_type.id,
            "event_date": base_date,
            "description": "custom-jan",
            "medical_record_id": record_a.id,
        },
        {
            "event_type_id": custom_type.id,
            "event_date": base_date + timedelta(days=10),
            "description": "custom-feb",
            "medical_record_id": record_a.id,
        },
        {
            "event_type_id": "vaccine_expirations",
            "event_date": base_date + timedelta(days=20),
            "description": "vaccine-mar",
            "medical_record_id": record_b.id,
        },
        {
            "event_type_id": follow_type.id,
            "event_date": base_date + timedelta(days=30),
            "description": "follow-apr",
            "medical_record_id": record_c.id,
        },
        {
            "event_type_id": custom_type.id,
            "event_date": base_date + timedelta(days=35),
            "description": "custom-apr",
            "medical_record_id": record_c.id,
        },
    ]

    for info in events_payload:
        _add_event(db_session, **info)

    db_session.commit()
    dates_by_description = {
        info["description"]: info["event_date"] for info in events_payload
    }
    return {
        "records": {
            "record_a": record_a.id,
            "record_b": record_b.id,
            "record_c": record_c.id,
        },
        "event_type_ids": {
            "custom": custom_type.id,
            "follow": follow_type.id,
        },
        "events": events_payload,
        "dates": dates_by_description,
    }


def test_get_events_initially_empty(client: TestClient) -> None:
    response = client.get("/events")
    assert response.status_code == 200
    payload = response.json()
    assert payload["events"] == []
    assert payload["total"] == 0
    assert payload["page"] == 1
    assert payload["page_size"] == 20


def test_get_events_supports_pagination(
    client: TestClient, db_session: Session
) -> None:
    _ensure_event_type(db_session, "custom_type", "CUSTOM_TYPE")
    for idx in range(5):
        _add_event(
            db_session,
            event_type_id="custom_type",
            event_date=date.today() + timedelta(days=idx),
            description=f"event-{idx}",
        )

    response = client.get("/events", params={"page": 2, "page_size": 2})
    payload = response.json()
    assert response.status_code == 200
    assert payload["total"] == 5
    assert payload["page"] == 2
    assert payload["page_size"] == 2
    assert len(payload["events"]) == 2


def test_get_events_page_out_of_range_returns_empty(
    client: TestClient, db_session: Session
) -> None:
    _ensure_event_type(db_session, "custom_type", "CUSTOM_TYPE")
    for idx in range(3):
        _add_event(
            db_session,
            event_type_id="custom_type",
            event_date=date.today() + timedelta(days=idx),
            description=f"event-{idx}",
        )

    response = client.get("/events", params={"page": 5, "page_size": 5})
    payload = response.json()
    assert response.status_code == 200
    assert payload["total"] == 3
    assert payload["events"] == []


def test_get_events_filters_by_event_type(client: TestClient, seeded_events) -> None:
    response = client.get(
        "/events",
        params={"event_type_ids": [seeded_events["event_type_ids"]["custom"]]},
    )
    payload = response.json()
    assert response.status_code == 200
    assert payload["total"] == 3
    assert all(
        event["type"]["id"] == seeded_events["event_type_ids"]["custom"]
        for event in payload["events"]
    )


def test_get_events_filters_by_medical_record(
    client: TestClient, seeded_events
) -> None:
    record_id = seeded_events["records"]["record_a"]
    response = client.get("/events", params={"medical_record_ids": [str(record_id)]})
    payload = response.json()
    assert response.status_code == 200
    assert payload["total"] == 2
    assert all(
        event["type"]["id"] == seeded_events["event_type_ids"]["custom"]
        for event in payload["events"]
    )


def test_get_events_filters_by_date_range(client: TestClient, seeded_events) -> None:
    dates = seeded_events["dates"]
    start_date = (dates["custom-feb"] - timedelta(days=1)).isoformat()
    end_date = dates["follow-apr"].isoformat()
    response = client.get(
        "/events",
        params={"start_date": start_date, "end_date": end_date},
    )
    payload = response.json()
    assert response.status_code == 200
    descriptions = {event["description"] for event in payload["events"]}
    assert descriptions == {"custom-feb", "vaccine-mar", "follow-apr"}


def test_get_events_filters_by_start_date_only(
    client: TestClient, seeded_events
) -> None:
    dates = seeded_events["dates"]
    start_date = (dates["vaccine-mar"] - timedelta(days=1)).isoformat()
    response = client.get("/events", params={"start_date": start_date})
    payload = response.json()
    assert response.status_code == 200
    descriptions = {event["description"] for event in payload["events"]}
    assert descriptions == {"vaccine-mar", "follow-apr", "custom-apr"}


def test_get_events_filters_by_end_date_only(client: TestClient, seeded_events) -> None:
    dates = seeded_events["dates"]
    response = client.get(
        "/events", params={"end_date": dates["custom-feb"].isoformat()}
    )
    payload = response.json()
    assert response.status_code == 200
    descriptions = {event["description"] for event in payload["events"]}
    assert descriptions == {"custom-jan", "custom-feb"}


def test_get_events_combines_filters(client: TestClient, seeded_events) -> None:
    record_id = seeded_events["records"]["record_c"]
    target_date = seeded_events["dates"]["custom-apr"]
    response = client.get(
        "/events",
        params={
            "event_type_ids": [seeded_events["event_type_ids"]["custom"]],
            "medical_record_ids": [str(record_id)],
            "start_date": target_date.isoformat(),
            "end_date": target_date.isoformat(),
        },
    )
    payload = response.json()
    assert response.status_code == 200
    assert payload["total"] == 1
    assert payload["events"][0]["description"] == "custom-apr"
