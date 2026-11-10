from app.ai.case_analysis import SECTIONS
from app.core.rbac import JUNIOR_ADVOCATE
from tests.conftest import add_user, login, make_org


def _owner(client, db, slug):
    make_org(db, slug, owner_email=f"owner@{slug}.pk", password="OwnerPass123!")
    assert login(client, slug, f"owner@{slug}.pk", "OwnerPass123!").status_code == 200


def _case(client, title="Murder reference", category="murder"):
    return client.post("/api/v1/cases", json={"title": title, "category": category}).json()["id"]


def test_generate_report_has_all_18_sections(client, db):
    _owner(client, db, "ca-gen")
    cid = _case(client)
    r = client.post(f"/api/v1/cases/{cid}/analysis")
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["status"] == "draft"  # never auto-approved
    report = body["report_json"]
    assert len(report) == len(SECTIONS) == 18
    for key, title in SECTIONS:
        assert key in report
        assert report[key]["title"] == title
    # Source references are present (built from indexed docs, not the model).
    assert "source_references" in report
    assert "lawyer_verification_questions" in report


def test_timeline_records_analysis(client, db):
    _owner(client, db, "ca-tl")
    cid = _case(client)
    client.post(f"/api/v1/cases/{cid}/analysis")
    types = [e["event_type"] for e in client.get(f"/api/v1/cases/{cid}/timeline").json()]
    assert "analysis_generated" in types


def test_approve_requires_grant_and_sets_status(client, db):
    org, _ = make_org(db, "ca-appr", owner_email="owner@caa.pk", password="OwnerPass123!")
    add_user(db, org.id, "junior@caa.pk", JUNIOR_ADVOCATE, password="JrPass123!")

    # Junior can request an analysis on their own case...
    assert login(client, "ca-appr", "junior@caa.pk", "JrPass123!").status_code == 200
    cid = _case(client, title="Jr case", category="theft")
    aid = client.post(f"/api/v1/cases/{cid}/analysis").json()["id"]
    # ...but cannot approve (no approvals:grant).
    assert client.post(f"/api/v1/cases/{cid}/analysis/{aid}/approve").status_code == 403

    # Owner (approvals:grant) approves it.
    client.cookies.clear()
    assert login(client, "ca-appr", "owner@caa.pk", "OwnerPass123!").status_code == 200
    r = client.post(f"/api/v1/cases/{cid}/analysis/{aid}/approve")
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "approved"
    assert r.json()["approved_by"] is not None


def test_analysis_tenant_isolation(client, db):
    _owner(client, db, "ca-a")
    cid = _case(client)
    client.post(f"/api/v1/cases/{cid}/analysis")

    make_org(db, "ca-b", owner_email="owner@cab.pk", password="PassB12345!")
    client.cookies.clear()
    assert login(client, "ca-b", "owner@cab.pk", "PassB12345!").status_code == 200
    # Org B cannot reach org A's case or its analyses.
    assert client.get(f"/api/v1/cases/{cid}/analysis").status_code == 404
