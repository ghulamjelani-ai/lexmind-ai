"""Cross-tenant isolation — the non-negotiable invariant: a user in one
organization must never see or affect another organization's data.
"""

from app.core.rbac import JUNIOR_ADVOCATE
from tests.conftest import add_user, login, make_org


def test_user_listing_is_scoped_to_own_org(client, db):
    org_a, _ = make_org(db, "tenant-a", owner_email="owner@a.pk", password="PassA12345!")
    add_user(db, org_a.id, "staff-a@a.pk", JUNIOR_ADVOCATE)

    org_b, _ = make_org(db, "tenant-b", owner_email="owner@b.pk", password="PassB12345!")
    add_user(db, org_b.id, "staff-b@b.pk", JUNIOR_ADVOCATE)

    # Owner A sees only org A's users.
    assert login(client, "tenant-a", "owner@a.pk", "PassA12345!").status_code == 200
    emails = {u["email"] for u in client.get("/api/v1/users").json()}
    assert "owner@a.pk" in emails
    assert "staff-a@a.pk" in emails
    assert "owner@b.pk" not in emails
    assert "staff-b@b.pk" not in emails
    # Every returned user belongs to org A.
    org_ids = {u["organization_id"] for u in client.get("/api/v1/users").json()}
    assert org_ids == {str(org_a.id)}


def test_cannot_login_to_other_org_with_own_credentials(client, db):
    make_org(db, "iso-a", owner_email="owner@isoa.pk", password="IsoPassA123!")
    make_org(db, "iso-b", owner_email="owner@isob.pk", password="IsoPassB123!")

    # Correct creds but wrong org slug must fail.
    assert login(client, "iso-b", "owner@isoa.pk", "IsoPassA123!").status_code == 401


def test_created_user_belongs_to_callers_org(client, db):
    org_a, _ = make_org(db, "create-a", owner_email="owner@ca.pk", password="CaPass1234!")
    make_org(db, "create-b", owner_email="owner@cb.pk", password="CbPass1234!")

    assert login(client, "create-a", "owner@ca.pk", "CaPass1234!").status_code == 200
    resp = client.post(
        "/api/v1/users",
        json={
            "email": "new@ca.pk",
            "full_name": "New A",
            "password": "NewPass1234!",
            "role": JUNIOR_ADVOCATE,
        },
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["organization_id"] == str(org_a.id)
