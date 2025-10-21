from datetime import date
from io import BytesIO
from pathlib import Path

from db.models.medical_record import MedicalRecord
from fastapi.testclient import TestClient

DATA_DIR = Path(__file__).parent / "data"


def test_full_medical_record_flow(client: TestClient, db_session) -> None:
    initial_types = client.get("/event-types").json()
    assert len(initial_types) == 4

    create_response = client.post(
        "/event-types",
        json={
            "name": "Sports Physical",
            "description": "School sports physical requirement",
        },
    )
    assert create_response.status_code == 201
    new_event_type_id = create_response.json()["id"]

    updated_types = client.get("/event-types").json()
    assert any(et["id"] == new_event_type_id for et in updated_types)

    pdf_path = next(DATA_DIR.glob("*.pdf"))
    with pdf_path.open("rb") as file_obj:
        upload_response = client.post(
            "/medical-records",
            files={"file": (pdf_path.name, file_obj, "application/pdf")},
        )

    assert upload_response.status_code == 200
    payload = upload_response.json()
    assert len(payload["events"]) == 1
    event = payload["events"][0]
    assert event["type"]["id"] == "vaccine_expirations"
    assert event["description"] == "test"
    assert date.fromisoformat(event["date"]) == date.today()

    events_response = client.get("/events")
    assert events_response.status_code == 200
    events_payload = events_response.json()
    assert len(events_payload["events"]) == 1
    assert events_payload["total"] == 1

    record_id = db_session.query(MedicalRecord).first().id
    delete_response = client.delete(f"/medical-records/{record_id}")
    assert delete_response.status_code == 204
    post_delete_events = client.get("/events").json()
    assert post_delete_events["events"] == []
    assert post_delete_events["total"] == 0

    remove_event_type = client.delete(f"/event-types/{new_event_type_id}")
    assert remove_event_type.status_code == 204
    final_types = client.get("/event-types").json()
    assert len(final_types) == 4
    assert all(et["id"] != new_event_type_id for et in final_types)


def test_e2e_error_flows(client: TestClient) -> None:
    invalid_upload = client.post(
        "/medical-records",
        files={"file": ("", BytesIO(b"pdf-bytes"), "application/pdf")},
    )
    assert invalid_upload.status_code == 400
    assert "Value error" in invalid_upload.json()["error"]

    missing_record = client.delete(
        "/medical-records/00000000-0000-0000-0000-000000000000"
    )
    assert missing_record.status_code == 400
    assert "not found" in missing_record.json()["error"]

    missing_event_type = client.delete("/event-types/does_not_exist")
    assert missing_event_type.status_code == 400
    assert "not found" in missing_event_type.json()["error"]

    protected_delete = client.delete("/event-types/vaccine_expirations")
    assert protected_delete.status_code == 400
    assert "not deletable" in protected_delete.json()["error"]
