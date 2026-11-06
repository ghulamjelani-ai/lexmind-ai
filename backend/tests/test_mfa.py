import pyotp

from tests.conftest import login, make_org


def test_mfa_enroll_activate_and_login_enforcement(client, db):
    make_org(db, "mfa-org", owner_email="owner@mfa.pk", password="OwnerPass123!")
    assert login(client, "mfa-org", "owner@mfa.pk", "OwnerPass123!").status_code == 200

    # Enroll -> get secret.
    resp = client.post("/api/v1/auth/mfa/enroll")
    assert resp.status_code == 200, resp.text
    secret = resp.json()["secret"]
    assert resp.json()["otpauth_uri"].startswith("otpauth://")

    totp = pyotp.TOTP(secret)

    # Activate with a valid code.
    assert client.post("/api/v1/auth/mfa/activate", json={"code": totp.now()}).status_code == 200

    # New login now requires the MFA code.
    client.cookies.clear()
    no_code = login(client, "mfa-org", "owner@mfa.pk", "OwnerPass123!")
    assert no_code.status_code == 401

    with_code = client.post(
        "/api/v1/auth/login",
        json={
            "org_slug": "mfa-org",
            "email": "owner@mfa.pk",
            "password": "OwnerPass123!",
            "mfa_code": totp.now(),
        },
    )
    assert with_code.status_code == 200, with_code.text


def test_mfa_activate_rejects_bad_code(client, db):
    make_org(db, "mfa-bad", owner_email="owner@mfab.pk", password="OwnerPass123!")
    assert login(client, "mfa-bad", "owner@mfab.pk", "OwnerPass123!").status_code == 200
    client.post("/api/v1/auth/mfa/enroll")
    assert client.post("/api/v1/auth/mfa/activate", json={"code": "000000"}).status_code == 400
