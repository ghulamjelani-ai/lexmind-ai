from app.core.rbac import CLERK
from tests.conftest import add_user, login, make_org


def _owner(client, db, slug):
    make_org(db, slug, owner_email=f"owner@{slug}.pk", password="OwnerPass123!")
    assert login(client, slug, f"owner@{slug}.pk", "OwnerPass123!").status_code == 200


def _case(client, title="Evidence matter", category="theft"):
    return client.post("/api/v1/cases", json={"title": title, "category": category}).json()["id"]


def test_evidence_analysis_has_all_keys(client, db):
    _owner(client, db, "ev-keys")
    cid = _case(client)
    r = client.post(f"/api/v1/cases/{cid}/evidence-analysis")
    assert r.status_code == 200, r.text
    body = r.json()
    for key in ("supporting", "contradicting", "missing", "notes", "chunks_used"):
        assert key in body
    assert isinstance(body["supporting"], list)
    assert isinstance(body["notes"], str)


def test_evidence_analysis_no_docs_notes_gap(client, db):
    _owner(client, db, "ev-empty")
    cid = _case(client)
    body = client.post(f"/api/v1/cases/{cid}/evidence-analysis").json()
    # With nothing indexed the agent must say so rather than invent evidence.
    assert body["chunks_used"] == 0
    assert body["notes"]


def test_evidence_analysis_requires_permission(client, db):
    org, _ = make_org(db, "ev-perm", owner_email="owner@evp.pk", password="OwnerPass123!")
    add_user(db, org.id, "clerk@evp.pk", CLERK, password="ClerkPass1!")
    assert login(client, "ev-perm", "owner@evp.pk", "OwnerPass123!").status_code == 200
    cid = _case(client)
    # Clerk lacks ai:analysis:request.
    client.cookies.clear()
    assert login(client, "ev-perm", "clerk@evp.pk", "ClerkPass1!").status_code == 200
    assert client.post(f"/api/v1/cases/{cid}/evidence-analysis").status_code in (403, 404)


def test_evidence_analysis_tenant_isolation(client, db):
    _owner(client, db, "ev-a")
    cid = _case(client)
    make_org(db, "ev-b", owner_email="owner@evb.pk", password="PassB12345!")
    client.cookies.clear()
    assert login(client, "ev-b", "owner@evb.pk", "PassB12345!").status_code == 200
    assert client.post(f"/api/v1/cases/{cid}/evidence-analysis").status_code == 404
