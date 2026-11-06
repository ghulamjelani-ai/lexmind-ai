from app.services import password_reset_service
from tests.conftest import login, make_org


def test_password_reset_flow(client, db):
    make_org(db, "reset-org", owner_email="owner@reset.pk", password="OldPass123!")

    # Request endpoint never reveals existence.
    r = client.post(
        "/api/v1/auth/password-reset/request",
        json={"org_slug": "reset-org", "email": "owner@reset.pk"},
    )
    assert r.status_code == 200

    # Obtain the raw token via the service (endpoint delivers it out-of-band).
    token = password_reset_service.request_reset(db, "reset-org", "owner@reset.pk")
    db.commit()
    assert token

    # Confirm with the token + new password.
    c = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": token, "new_password": "NewPass456!"},
    )
    assert c.status_code == 200, c.text

    # Old password fails, new one works.
    assert login(client, "reset-org", "owner@reset.pk", "OldPass123!").status_code == 401
    assert login(client, "reset-org", "owner@reset.pk", "NewPass456!").status_code == 200


def test_password_reset_request_unknown_is_generic(client, db):
    # Unknown org/email still returns 200 (no enumeration).
    r = client.post(
        "/api/v1/auth/password-reset/request",
        json={"org_slug": "nope", "email": "ghost@nowhere.pk"},
    )
    assert r.status_code == 200


def test_password_reset_confirm_bad_token(client, db):
    assert (
        client.post(
            "/api/v1/auth/password-reset/confirm",
            json={"token": "not-a-real-token", "new_password": "Whatever123!"},
        ).status_code
        == 400
    )
