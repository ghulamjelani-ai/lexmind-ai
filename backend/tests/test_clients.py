from app.core.rbac import JUNIOR_ADVOCATE
from tests.conftest import add_user, login, make_org


def _auth_owner(client, db, slug="cl-org"):
    make_org(db, slug, owner_email=f"owner@{slug}.pk", password="OwnerPass123!")
    assert login(client, slug, f"owner@{slug}.pk", "OwnerPass123!").status_code == 200


def test_client_crud(client, db):
    _auth_owner(client, db, "cl-crud")
    r = client.post(
        "/api/v1/clients", json={"full_name": "Ayesha Malik", "cnic": "35202-1234567-1"}
    )
    assert r.status_code == 201, r.text
    cid = r.json()["id"]
    assert r.json()["has_cnic"] is True  # CNIC stored, not echoed

    assert client.get(f"/api/v1/clients/{cid}").json()["full_name"] == "Ayesha Malik"

    page = client.get("/api/v1/clients").json()
    assert page["total"] == 1 and len(page["items"]) == 1

    assert client.patch(f"/api/v1/clients/{cid}", json={"phone": "0300-1234567"}).status_code == 200
    assert client.get(f"/api/v1/clients/{cid}").json()["phone"] == "0300-1234567"

    assert client.delete(f"/api/v1/clients/{cid}").status_code == 204
    assert client.get(f"/api/v1/clients/{cid}").status_code == 404


def test_client_input_validation(client, db):
    _auth_owner(client, db, "cl-valid")

    # CNIC must be 13 digits.
    assert client.post(
        "/api/v1/clients", json={"full_name": "Bad CNIC", "cnic": "123"}
    ).status_code == 422
    # A valid CNIC with dashes is accepted (formatting preserved).
    assert client.post(
        "/api/v1/clients", json={"full_name": "Good CNIC", "cnic": "35202-1234567-1"}
    ).status_code == 201

    # Garbage phone is rejected; a sensible one is accepted.
    assert client.post(
        "/api/v1/clients", json={"full_name": "Bad Phone", "phone": "abc"}
    ).status_code == 422
    assert client.post(
        "/api/v1/clients", json={"full_name": "Good Phone", "phone": "+92 300 1234567"}
    ).status_code == 201

    # Empty optional strings are treated as omitted, not invalid.
    assert client.post(
        "/api/v1/clients", json={"full_name": "No Email", "email": "", "cnic": ""}
    ).status_code == 201


def test_conflict_check(client, db):
    _auth_owner(client, db, "cl-conf")
    client.post("/api/v1/clients", json={"full_name": "Imran Ahmed"})
    client.post(
        "/api/v1/cases",
        json={"title": "State vs X", "category": "criminal", "opposite_party": "Imran Ahmed"},
    )

    res = client.get("/api/v1/clients/conflict-check", params={"name": "Imran"}).json()
    assert res["has_conflict"] is True
    kinds = {m["kind"] for m in res["matches"]}
    assert "existing_client" in kinds
    assert "opposing_party" in kinds

    clean = client.get("/api/v1/clients/conflict-check", params={"name": "Nobody Here"}).json()
    assert clean["has_conflict"] is False


def test_clients_require_permission(client, db):
    org, _ = make_org(db, "cl-authz", owner_email="owner@cla.pk", password="OwnerPass123!")
    add_user(db, org.id, "junior@cla.pk", JUNIOR_ADVOCATE, password="JrPass123!")
    assert login(client, "cl-authz", "junior@cla.pk", "JrPass123!").status_code == 200
    # Junior lacks clients:manage.
    assert client.get("/api/v1/clients").status_code == 403
    assert client.post("/api/v1/clients", json={"full_name": "X"}).status_code == 403


def test_client_tenant_isolation(client, db):
    org_a, _ = make_org(db, "cl-a", owner_email="owner@cla2.pk", password="PassA12345!")
    make_org(db, "cl-b", owner_email="owner@clb2.pk", password="PassB12345!")

    assert login(client, "cl-a", "owner@cla2.pk", "PassA12345!").status_code == 200
    cid = client.post("/api/v1/clients", json={"full_name": "Org A Client"}).json()["id"]

    client.cookies.clear()
    assert login(client, "cl-b", "owner@clb2.pk", "PassB12345!").status_code == 200
    assert client.get(f"/api/v1/clients/{cid}").status_code == 404
    assert client.get("/api/v1/clients").json()["total"] == 0
