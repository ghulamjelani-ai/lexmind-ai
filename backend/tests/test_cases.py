from app.core.rbac import JUNIOR_ADVOCATE
from tests.conftest import add_user, login, make_org


def _owner(client, db, slug):
    make_org(db, slug, owner_email=f"owner@{slug}.pk", password="OwnerPass123!")
    assert login(client, slug, f"owner@{slug}.pk", "OwnerPass123!").status_code == 200


def test_create_list_get_case(client, db):
    _owner(client, db, "cs-basic")
    r = client.post("/api/v1/cases", json={"title": "Bail Application", "category": "bail"})
    assert r.status_code == 201, r.text
    cid = r.json()["id"]
    assert r.json()["status"] == "open"
    assert r.json()["assigned_lawyer_id"] is not None  # creator is primary

    page = client.get("/api/v1/cases").json()
    assert page["total"] == 1 and page["items"][0]["id"] == cid

    assert client.get(f"/api/v1/cases/{cid}").json()["title"] == "Bail Application"


def test_case_create_rejects_bad_category(client, db):
    _owner(client, db, "cs-cat")
    r = client.post("/api/v1/cases", json={"title": "X", "category": "not-a-category"})
    assert r.status_code == 422


def test_timeline_records_events(client, db):
    _owner(client, db, "cs-tl")
    cid = client.post("/api/v1/cases", json={"title": "Case TL", "category": "civil"}).json()["id"]
    client.patch(f"/api/v1/cases/{cid}", json={"status": "in_hearing"})
    client.post(f"/api/v1/cases/{cid}/notes", json={"note": "Client called"})

    events = client.get(f"/api/v1/cases/{cid}/timeline").json()
    types = [e["event_type"] for e in events]
    assert "case_created" in types
    assert "status_changed" in types
    assert "note_added" in types


def test_scope_assigned_hides_other_cases(client, db):
    org, _ = make_org(db, "cs-scope", owner_email="owner@css.pk", password="OwnerPass123!")
    add_user(db, org.id, "j1@css.pk", JUNIOR_ADVOCATE, password="J1Pass123!")
    add_user(db, org.id, "j2@css.pk", JUNIOR_ADVOCATE, password="J2Pass123!")

    # Junior 1 creates a case -> auto-assigned primary, so visible to them.
    assert login(client, "cs-scope", "j1@css.pk", "J1Pass123!").status_code == 200
    cid = client.post("/api/v1/cases", json={"title": "J1 Case", "category": "theft"}).json()["id"]
    assert client.get("/api/v1/cases").json()["total"] == 1

    # Junior 2 (assigned scope) must not see J1's case.
    client.cookies.clear()
    assert login(client, "cs-scope", "j2@css.pk", "J2Pass123!").status_code == 200
    assert client.get("/api/v1/cases").json()["total"] == 0
    assert client.get(f"/api/v1/cases/{cid}").status_code == 404

    # Owner (all scope) sees it.
    client.cookies.clear()
    assert login(client, "cs-scope", "owner@css.pk", "OwnerPass123!").status_code == 200
    assert client.get(f"/api/v1/cases/{cid}").status_code == 200


def test_assignment_grants_access(client, db):
    org, _ = make_org(db, "cs-assign", owner_email="owner@csa.pk", password="OwnerPass123!")
    j2 = add_user(db, org.id, "j2@csa.pk", JUNIOR_ADVOCATE, password="J2Pass123!")

    assert login(client, "cs-assign", "owner@csa.pk", "OwnerPass123!").status_code == 200
    cid = client.post("/api/v1/cases", json={"title": "Shared", "category": "fraud"}).json()["id"]

    # Assign j2 as supporting.
    r = client.post(
        f"/api/v1/cases/{cid}/assignments",
        json={"user_id": str(j2.id), "role_on_case": "supporting"},
    )
    assert r.status_code == 201, r.text

    # j2 can now see the case.
    client.cookies.clear()
    assert login(client, "cs-assign", "j2@csa.pk", "J2Pass123!").status_code == 200
    assert client.get(f"/api/v1/cases/{cid}").status_code == 200


def test_junior_cannot_delete_case(client, db):
    org, _ = make_org(db, "cs-del", owner_email="owner@csd.pk", password="OwnerPass123!")
    add_user(db, org.id, "j@csd.pk", JUNIOR_ADVOCATE, password="JPass123!")
    assert login(client, "cs-del", "j@csd.pk", "JPass123!").status_code == 200
    cid = client.post("/api/v1/cases", json={"title": "Jr Case", "category": "civil"}).json()["id"]
    # Junior has cases:create/read/update but not cases:delete.
    assert client.delete(f"/api/v1/cases/{cid}").status_code == 403


def test_case_tenant_isolation(client, db):
    make_org(db, "cs-a", owner_email="owner@csa2.pk", password="PassA12345!")
    make_org(db, "cs-b", owner_email="owner@csb2.pk", password="PassB12345!")

    assert login(client, "cs-a", "owner@csa2.pk", "PassA12345!").status_code == 200
    cid = client.post("/api/v1/cases", json={"title": "A Case", "category": "civil"}).json()["id"]

    client.cookies.clear()
    assert login(client, "cs-b", "owner@csb2.pk", "PassB12345!").status_code == 200
    assert client.get(f"/api/v1/cases/{cid}").status_code == 404
    assert client.get("/api/v1/cases").json()["total"] == 0
