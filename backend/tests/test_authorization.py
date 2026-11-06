from app.core.rbac import JUNIOR_ADVOCATE
from tests.conftest import add_user, login, make_org


def test_unauthenticated_cannot_list_users(client):
    assert client.get("/api/v1/users").status_code == 401


def test_junior_cannot_manage_users(client, db):
    org, _owner = make_org(db, "authz-org", owner_email="owner@authz.pk")
    add_user(db, org.id, "junior@authz.pk", JUNIOR_ADVOCATE, password="JrPass123!")

    assert login(client, "authz-org", "junior@authz.pk", "JrPass123!").status_code == 200
    # Junior lacks admin:users:manage.
    assert client.get("/api/v1/users").status_code == 403
    resp = client.post(
        "/api/v1/users",
        json={
            "email": "new@authz.pk",
            "full_name": "New",
            "password": "NewPass123!",
            "role": JUNIOR_ADVOCATE,
        },
    )
    assert resp.status_code == 403


def test_owner_can_manage_users(client, db):
    make_org(db, "owner-authz", owner_email="owner@o.pk", password="OwnerPass123!")
    assert login(client, "owner-authz", "owner@o.pk", "OwnerPass123!").status_code == 200

    assert client.get("/api/v1/users").status_code == 200
    resp = client.post(
        "/api/v1/users",
        json={
            "email": "staff@o.pk",
            "full_name": "Staff",
            "password": "StaffPass123!",
            "role": JUNIOR_ADVOCATE,
        },
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["email"] == "staff@o.pk"
