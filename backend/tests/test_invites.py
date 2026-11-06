from app.core.rbac import JUNIOR_ADVOCATE
from tests.conftest import login, make_org


def test_invite_create_and_accept(client, db):
    make_org(db, "inv-org", owner_email="owner@inv.pk", password="OwnerPass123!")
    assert login(client, "inv-org", "owner@inv.pk", "OwnerPass123!").status_code == 200

    created = client.post(
        "/api/v1/invites", json={"email": "newbie@inv.pk", "role": JUNIOR_ADVOCATE}
    )
    assert created.status_code == 201, created.text
    token = created.json()["token"]

    # Accept is public (no auth). Use a clean client.
    client.cookies.clear()
    accepted = client.post(
        "/api/v1/invites/accept",
        json={"token": token, "full_name": "New Bie", "password": "NewbiePass123!"},
    )
    assert accepted.status_code == 201, accepted.text
    assert accepted.json()["email"] == "newbie@inv.pk"

    # The new user can log in.
    assert login(client, "inv-org", "newbie@inv.pk", "NewbiePass123!").status_code == 200


def test_invite_requires_permission(client, db):
    org, _ = make_org(db, "inv-authz", owner_email="owner@inva.pk", password="OwnerPass123!")
    from tests.conftest import add_user

    add_user(db, org.id, "junior@inva.pk", JUNIOR_ADVOCATE, password="JrPass123!")
    assert login(client, "inv-authz", "junior@inva.pk", "JrPass123!").status_code == 200
    # Junior lacks admin:users:manage.
    resp = client.post("/api/v1/invites", json={"email": "x@inva.pk", "role": JUNIOR_ADVOCATE})
    assert resp.status_code == 403


def test_accept_invalid_token(client, db):
    resp = client.post(
        "/api/v1/invites/accept",
        json={"token": "bogus-token-value", "full_name": "X", "password": "Passw0rd123!"},
    )
    assert resp.status_code == 400
