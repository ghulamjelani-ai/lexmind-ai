from app.core.config import get_settings
from tests.conftest import login, make_org

COOKIE = get_settings().session_cookie_name


def test_register_org_and_login(client, db):
    resp = client.post(
        "/api/v1/orgs/register",
        json={
            "org_name": "Acme Law",
            "org_slug": "acme-law",
            "owner_name": "Owner",
            "owner_email": "owner@acme.pk",
            "owner_password": "OwnerPass123!",
        },
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["slug"] == "acme-law"

    resp = login(client, "acme-law", "owner@acme.pk", "OwnerPass123!")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["user"]["email"] == "owner@acme.pk"
    assert "admin:users:manage" in body["permissions"]
    assert COOKIE in resp.cookies


def test_login_wrong_password(client, db):
    make_org(db, "wrong-pass", owner_email="o@x.pk", password="RightPass123!")
    resp = login(client, "wrong-pass", "o@x.pk", "WrongPass123!")
    assert resp.status_code == 401


def test_login_unknown_org(client):
    resp = login(client, "nope", "o@x.pk", "whatever123")
    assert resp.status_code == 401


def test_me_requires_auth(client):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_and_logout_flow(client, db):
    make_org(db, "flow-org", owner_email="o@flow.pk", password="FlowPass123!")
    assert login(client, "flow-org", "o@flow.pk", "FlowPass123!").status_code == 200

    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["user"]["email"] == "o@flow.pk"

    assert client.post("/api/v1/auth/logout").status_code == 200
    # Cookie cleared -> session gone.
    client.cookies.clear()
    assert client.get("/api/v1/auth/me").status_code == 401
