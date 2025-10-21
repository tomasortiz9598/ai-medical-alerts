from pathlib import Path

import pytest
from db.models.medical_record import MedicalRecord
from fastapi.testclient import TestClient

DATA_DIR = Path(__file__).resolve().parents[2] / "tests" / "data"


@pytest.mark.parametrize(
    "pdf_path",
    sorted(DATA_DIR.glob("*.pdf")),
    ids=lambda path: path.name,
)
def test_upload_medical_record_returns_events(
    client: TestClient, pdf_path: Path
) -> None:
    with pdf_path.open("rb") as file_obj:
        response = client.post(
            "/medical-records",
            files={"file": (pdf_path.name, file_obj, "application/pdf")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["events"], "Expected at least one event"


def test_delete_medical_record_removes_entry(client: TestClient, db_session) -> None:
    pdf_path = next(DATA_DIR.glob("*.pdf"))
    with pdf_path.open("rb") as file_obj:
        client.post(
            "/medical-records",
            files={"file": (pdf_path.name, file_obj, "application/pdf")},
        )

    record_id = db_session.query(MedicalRecord).first().id
    delete_response = client.delete(f"/medical-records/{record_id}")
    assert delete_response.status_code == 204
    assert db_session.query(MedicalRecord).count() == 0


def test_upload_with_blank_filename_returns_validation_error(
    client: TestClient,
) -> None:
    response = client.post(
        "/medical-records",
        files={"file": ("", b"data", "application/pdf")},
    )
    assert response.status_code == 400
    assert "Value error" in response.json()["error"]


def test_delete_missing_medical_record_returns_error(client: TestClient) -> None:
    response = client.delete("/medical-records/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 400
    assert "not found" in response.json()["error"]
