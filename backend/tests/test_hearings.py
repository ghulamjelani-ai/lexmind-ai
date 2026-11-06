from tests.conftest import login, make_org


def _owner_with_case(client, db, slug):
    make_org(db, slug, owner_email=f"owner@{slug}.pk", password="OwnerPass123!")
    assert login(client, slug, f"owner@{slug}.pk", "OwnerPass123!").status_code == 200
    return client.post("/api/v1/cases", json={"title": "Case H", "category": "civil"}).json()["id"]


def test_hearing_is_unconfirmed_until_confirmed(client, db):
    cid = _owner_with_case(client, db, "hr-org")
    r = client.post(
        f"/api/v1/cases/{cid}/hearings",
        json={"scheduled_at": "2026-12-01T10:00:00Z", "court_name": "LHC"},
    )
    assert r.status_code == 201, r.text
    hid = r.json()["id"]
    # Honesty rule: a manually-entered hearing is unconfirmed.
    assert r.json()["status"] == "unconfirmed"

    conf = client.post(
        f"/api/v1/hearings/{hid}/confirm", json={"confirmation_source": "LHC cause list"}
    )
    assert conf.status_code == 200
    assert conf.json()["status"] == "confirmed"
    assert conf.json()["confirmation_source"] == "LHC cause list"


def test_hearing_shows_on_calendar(client, db):
    cid = _owner_with_case(client, db, "hr-cal")
    client.post(
        f"/api/v1/cases/{cid}/hearings",
        json={"scheduled_at": "2026-12-05T09:30:00Z", "court_name": "District Court"},
    )
    items = client.get(
        "/api/v1/calendar", params={"from": "2026-12-01T00:00:00Z", "to": "2026-12-31T23:59:59Z"}
    ).json()
    hearings = [i for i in items if i["kind"] == "hearing"]
    assert len(hearings) == 1
    assert hearings[0]["case_id"] == cid


def test_hearing_creates_timeline_event(client, db):
    cid = _owner_with_case(client, db, "hr-tl")
    client.post(f"/api/v1/cases/{cid}/hearings", json={"scheduled_at": "2026-12-10T10:00:00Z"})
    types = [e["event_type"] for e in client.get(f"/api/v1/cases/{cid}/timeline").json()]
    assert "hearing_scheduled" in types
