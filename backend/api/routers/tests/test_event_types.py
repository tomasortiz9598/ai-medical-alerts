from fastapi.testclient import TestClient


def test_get_event_types_returns_seeded_defaults(client: TestClient) -> None:
    response = client.get("/event-types")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 4
    ids = {item["id"] for item in payload}
    assert ids == {
        "vaccine_expirations",
        "upcoming_dental_procedures",
        "routine_exams",
        "follow_up_appointments",
    }


def test_create_event_type_adds_new_entry(client: TestClient) -> None:
    response = client.post(
        "/event-types",
        json={"name": "Lab Visits", "description": "Future lab appointments"},
    )
    assert response.status_code == 201
    created = response.json()
    assert created["id"] == "lab_visits"
    follow_up = client.get("/event-types").json()
    assert any(item["id"] == "lab_visits" for item in follow_up)


def test_delete_event_type_removes_custom_entry(client: TestClient) -> None:
    client.post(
        "/event-types",
        json={"name": "Derm Check", "description": "Dermatology follow up"},
    )
    response = client.delete("/event-types/derm_check")
    assert response.status_code == 204
    remaining_ids = {item["id"] for item in client.get("/event-types").json()}
    assert "derm_check" not in remaining_ids


def test_delete_event_type_nonexistent_returns_error(client: TestClient) -> None:
    response = client.delete("/event-types/not_real")
    assert response.status_code == 400
    assert "not found" in response.json()["error"]


def test_delete_non_deletable_event_type_rejected(client: TestClient) -> None:
    response = client.delete("/event-types/vaccine_expirations")
    assert response.status_code == 400
    assert "not deletable" in response.json()["error"]
