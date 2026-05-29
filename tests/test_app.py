"""Tests for the Activity Tracker API.

Some of these tests currently FAIL. That is expected -
the failures point to the bugs you need to fix.

Run with: pytest -v
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import storage


@pytest.fixture(autouse=True)
def reset_storage():
    storage.reset()
    yield
    storage.reset()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def user(client):
    response = client.post(
        "/users", json={"email": "alice@example.com", "name": "Alice"}
    )
    assert response.status_code == 201
    return response.json()


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_user_returns_payload(client):
    response = client.post("/users", json={"email": "bob@example.com", "name": "Bob"})
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "bob@example.com"
    assert body["name"] == "Bob"
    assert "id" in body


def test_get_user_by_id(client, user):
    response = client.get(f"/users/{user['id']}")
    assert response.status_code == 200
    assert response.json()["email"] == user["email"]


def test_get_user_missing_returns_404(client):
    response = client.get("/users/9999")
    assert response.status_code == 404


def test_create_event_returns_201(client, user):
    response = client.post(
        "/events",
        json={"user_id": user["id"], "event_type": "login", "metadata": {}},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["event_type"] == "login"
    assert body["user_id"] == user["id"]


def test_create_event_with_unknown_user_returns_404(client):
    response = client.post(
        "/events",
        json={"user_id": 9999, "event_type": "login", "metadata": {}},
    )
    assert response.status_code == 404


def test_list_events_includes_created_items(client, user):
    for event_type in ["login", "page_view", "click", "page_view", "logout"]:
        client.post(
            "/events",
            json={"user_id": user["id"], "event_type": event_type, "metadata": {}},
        )

    response = client.get("/events?offset=0&limit=10")
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 5


def test_list_events_paginates_without_overlap(client, user):
    for i in range(10):
        client.post(
            "/events",
            json={"user_id": user["id"], "event_type": "click", "metadata": {"i": i}},
        )

    page1 = client.get("/events?offset=0&limit=5").json()
    page2 = client.get("/events?offset=5&limit=5").json()

    assert len(page1) == 5
    assert len(page2) == 5
    page1_ids = {e["id"] for e in page1}
    page2_ids = {e["id"] for e in page2}
    assert page1_ids.isdisjoint(page2_ids), "Pages should not overlap"


def test_list_events_hides_soft_deleted_items(client, user):
    created_ids = []
    for _ in range(3):
        response = client.post(
            "/events",
            json={"user_id": user["id"], "event_type": "click", "metadata": {}},
        )
        created_ids.append(response.json()["id"])

    delete_response = client.delete(f"/events/{created_ids[1]}")
    assert delete_response.status_code == 204

    response = client.get("/events?offset=0&limit=10")
    assert response.status_code == 200
    remaining_ids = {e["id"] for e in response.json()}
    assert created_ids[1] not in remaining_ids
    assert len(response.json()) == 2


def test_delete_missing_event_returns_404(client):
    response = client.delete("/events/9999")
    assert response.status_code == 404


def test_delete_same_event_twice_changes_response(client, user):
    create_response = client.post(
        "/events",
        json={"user_id": user["id"], "event_type": "click", "metadata": {}},
    )
    event_id = create_response.json()["id"]

    first_delete = client.delete(f"/events/{event_id}")
    second_delete = client.delete(f"/events/{event_id}")

    assert first_delete.status_code == 204
    assert second_delete.status_code == 404


def test_pagination_after_delete_stays_consistent(client, user):
    created_ids = []
    for i in range(6):
        response = client.post(
            "/events",
            json={"user_id": user["id"], "event_type": "click", "metadata": {"i": i}},
        )
        created_ids.append(response.json()["id"])

    delete_response = client.delete(f"/events/{created_ids[2]}")
    assert delete_response.status_code == 204

    page1 = client.get("/events?offset=0&limit=3")
    page2 = client.get("/events?offset=3&limit=3")

    assert page1.status_code == 200
    assert page2.status_code == 200

    page1_ids = [event["id"] for event in page1.json()]
    page2_ids = [event["id"] for event in page2.json()]

    assert created_ids[2] not in page1_ids + page2_ids
    assert len(page1_ids) == 3
    assert len(page2_ids) == 2
    assert set(page1_ids).isdisjoint(page2_ids), "Pages should not overlap"


def test_get_user_events_no_since(client, user):
    # Create another user to verify we only get events for the target user
    other_user_res = client.post(
        "/users", json={"email": "other@example.com", "name": "Other"}
    )
    assert other_user_res.status_code == 201
    other_user_id = other_user_res.json()["id"]

    # Post events for target user
    e1 = client.post(
        "/events",
        json={"user_id": user["id"], "event_type": "login", "metadata": {}},
    ).json()
    e2 = client.post(
        "/events",
        json={"user_id": user["id"], "event_type": "click", "metadata": {}},
    ).json()

    # Post event for other user
    client.post(
        "/events",
        json={"user_id": other_user_id, "event_type": "click", "metadata": {}},
    )

    # Call endpoint without since
    response = client.get(f"/users/{user['id']}/events")
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 2
    assert events[0]["id"] == e1["id"]
    assert events[1]["id"] == e2["id"]


def test_get_user_events_user_missing(client):
    response = client.get("/users/9999/events")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_get_user_events_excludes_soft_deleted(client, user):
    e1 = client.post(
        "/events",
        json={"user_id": user["id"], "event_type": "login", "metadata": {}},
    ).json()
    e2 = client.post(
        "/events",
        json={"user_id": user["id"], "event_type": "click", "metadata": {}},
    ).json()

    # Soft delete the first event
    delete_res = client.delete(f"/events/{e1['id']}")
    assert delete_res.status_code == 204

    # Call endpoint
    response = client.get(f"/users/{user['id']}/events")
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 1
    assert events[0]["id"] == e2["id"]


def test_get_user_events_with_since(client, user):
    from datetime import datetime, timezone

    # Post 2 events
    e1 = client.post(
        "/events",
        json={"user_id": user["id"], "event_type": "login", "metadata": {}},
    ).json()
    e2 = client.post(
        "/events",
        json={"user_id": user["id"], "event_type": "click", "metadata": {}},
    ).json()

    # Modify created_at manually in storage to guarantee deterministic values
    t1 = datetime(2026, 5, 29, 12, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 5, 29, 13, 0, 0, tzinfo=timezone.utc)
    storage.get_event(e1["id"]).created_at = t1
    storage.get_event(e2["id"]).created_at = t2

    # Case 1: since is timezone-aware UTC in between t1 and t2
    # Expect only event 2
    res_aware = client.get(f"/users/{user['id']}/events?since=2026-05-29T12:30:00Z")
    assert res_aware.status_code == 200
    events_aware = res_aware.json()
    assert len(events_aware) == 1
    assert events_aware[0]["id"] == e2["id"]

    # Case 2: since is timezone-aware +03:00 (equivalent to 12:30:00 UTC is 15:30:00+03:00)
    # Expect only event 2
    res_tz = client.get(f"/users/{user['id']}/events?since=2026-05-29T15:30:00%2B03:00")
    assert res_tz.status_code == 200
    events_tz = res_tz.json()
    assert len(events_tz) == 1
    assert events_tz[0]["id"] == e2["id"]

    # Case 3: since is naive datetime (defaults to UTC)
    # Expect only event 2
    res_naive = client.get(f"/users/{user['id']}/events?since=2026-05-29T12:30:00")
    assert res_naive.status_code == 200
    events_naive = res_naive.json()
    assert len(events_naive) == 1
    assert events_naive[0]["id"] == e2["id"]
