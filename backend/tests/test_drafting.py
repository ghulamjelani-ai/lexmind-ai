from app.core.rbac import JUNIOR_ADVOCATE
from tests.conftest import add_user, login, make_org


def _owner(client, db, slug):
    make_org(db, slug, owner_email=f"owner@{slug}.pk", password="OwnerPass123!")
    assert login(client, slug, f"owner@{slug}.pk", "OwnerPass123!").status_code == 200


def _case(client, title="Bail matter", category="bail"):
    return client.post("/api/v1/cases", json={"title": title, "category": category}).json()["id"]


def test_generate_draft_is_draft_with_review_disclaimer(client, db):
    _owner(client, db, "dr-gen")
    cid = _case(client)
    r = client.post(
        f"/api/v1/cases/{cid}/drafts",
        json={"draft_type": "bail_application", "title": "Bail application", "instructions": "x"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["status"] == "draft"  # never auto-approved/usable
    assert body["content"].startswith("DRAFT")  # review disclaimer is forced on
    assert body["draft_type"] == "bail_application"


def test_draft_records_timeline_event(client, db):
    _owner(client, db, "dr-tl")
    cid = _case(client)
    client.post(
        f"/api/v1/cases/{cid}/drafts",
        json={"draft_type": "legal_notice", "title": "Notice"},
    )
    types = [e["event_type"] for e in client.get(f"/api/v1/cases/{cid}/timeline").json()]
    assert "draft_generated" in types


def test_draft_approval_requires_grant(client, db):
    org, _ = make_org(db, "dr-appr", owner_email="owner@dra.pk", password="OwnerPass123!")
    add_user(db, org.id, "junior@dra.pk", JUNIOR_ADVOCATE, password="JrPass123!")

    assert login(client, "dr-appr", "junior@dra.pk", "JrPass123!").status_code == 200
    cid = _case(client, title="Jr draft", category="theft")
    did = client.post(
        f"/api/v1/cases/{cid}/drafts",
        json={"draft_type": "application", "title": "App"},
    ).json()["id"]
    # Junior can generate but cannot approve.
    assert client.post(f"/api/v1/cases/{cid}/drafts/{did}/approve").status_code == 403

    client.cookies.clear()
    assert login(client, "dr-appr", "owner@dra.pk", "OwnerPass123!").status_code == 200
    r = client.post(f"/api/v1/cases/{cid}/drafts/{did}/approve")
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "approved"
    assert r.json()["approved_by"] is not None


def test_draft_tenant_isolation(client, db):
    _owner(client, db, "dr-a")
    cid = _case(client)
    client.post(f"/api/v1/cases/{cid}/drafts", json={"draft_type": "x", "title": "t"})

    make_org(db, "dr-b", owner_email="owner@drb.pk", password="PassB12345!")
    client.cookies.clear()
    assert login(client, "dr-b", "owner@drb.pk", "PassB12345!").status_code == 200
    assert client.get(f"/api/v1/cases/{cid}/drafts").status_code == 404
