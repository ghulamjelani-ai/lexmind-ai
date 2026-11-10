from datetime import UTC, datetime, timedelta

from tests.conftest import login, make_org


def _owner(client, db, slug):
    make_org(db, slug, owner_email=f"owner@{slug}.pk", password="OwnerPass123!")
    assert login(client, slug, f"owner@{slug}.pk", "OwnerPass123!").status_code == 200


def _case(client, title="Hearing case"):
    return client.post("/api/v1/cases", json={"title": title, "category": "civil"}).json()["id"]


def _hearing(client, cid, when):
    return client.post(
        f"/api/v1/cases/{cid}/hearings", json={"scheduled_at": when.isoformat()}
    ).json()


def test_dispatch_creates_reminder_for_upcoming(client, db):
    _owner(client, db, "hr")
    cid = _case(client)
    _hearing(client, cid, datetime.now(tz=UTC) + timedelta(hours=12))
    r = client.post("/api/v1/hearings/reminders/dispatch")
    assert r.status_code == 200, r.text
    assert r.json()["reminders_created"] >= 1
    # The owner (case creator) has an unread hearing reminder.
    notes = client.get("/api/v1/notifications").json()
    items = notes["items"] if isinstance(notes, dict) else notes
    assert any(n["type"] == "hearing_reminder" for n in items)


def test_dispatch_is_idempotent(client, db):
    _owner(client, db, "hr-idem")
    cid = _case(client)
    _hearing(client, cid, datetime.now(tz=UTC) + timedelta(hours=10))
    first = client.post("/api/v1/hearings/reminders/dispatch").json()["reminders_created"]
    second = client.post("/api/v1/hearings/reminders/dispatch").json()["reminders_created"]
    assert first >= 1
    assert second == 0  # no duplicate reminders on a second run


def test_dispatch_ignores_far_and_past_hearings(client, db):
    _owner(client, db, "hr-window")
    cid = _case(client)
    _hearing(client, cid, datetime.now(tz=UTC) + timedelta(days=30))  # too far
    _hearing(client, cid, datetime.now(tz=UTC) - timedelta(hours=5))  # already past
    assert client.post("/api/v1/hearings/reminders/dispatch").json()["reminders_created"] == 0


def test_dispatch_requires_permission(client, db):
    _owner(client, db, "hr-perm")  # owner has hearings:manage; sanity that route is gated
    # A fresh client with no session cannot dispatch.
    client.cookies.clear()
    assert client.post("/api/v1/hearings/reminders/dispatch").status_code == 401
