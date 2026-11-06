import uuid

from app.core.rbac import JUNIOR_ADVOCATE
from tests.conftest import add_user, login, make_org


def test_approval_request_decide_and_notify(client, db):
    org, owner = make_org(db, "ap-org", owner_email="owner@ap.pk", password="OwnerPass123!")
    add_user(db, org.id, "j@ap.pk", JUNIOR_ADVOCATE, password="JPass123!")

    # Junior requests approval, naming the owner as approver.
    assert login(client, "ap-org", "j@ap.pk", "JPass123!").status_code == 200
    r = client.post(
        "/api/v1/approvals",
        json={
            "target_type": "document",
            "target_id": str(uuid.uuid4()),
            "approver_id": str(owner.id),
        },
    )
    assert r.status_code == 201, r.text
    aid = r.json()["id"]
    assert r.json()["status"] == "pending"
    # Junior lacks approvals:grant, so cannot list/decide.
    assert client.get("/api/v1/approvals").status_code == 403

    # Owner sees a notification + the pending approval, and approves it.
    client.cookies.clear()
    assert login(client, "ap-org", "owner@ap.pk", "OwnerPass123!").status_code == 200
    notifs = client.get("/api/v1/notifications").json()["items"]
    assert any(n["type"] == "approval.requested" for n in notifs)

    pending = client.get("/api/v1/approvals", params={"status": "pending"}).json()
    assert pending["total"] == 1
    dec = client.post(f"/api/v1/approvals/{aid}/decide", json={"approve": True})
    assert dec.status_code == 200
    assert dec.json()["status"] == "approved"

    # Deciding again is rejected.
    again = client.post(f"/api/v1/approvals/{aid}/decide", json={"approve": False})
    assert again.status_code == 400

    # Requester (junior) got a decision notification.
    client.cookies.clear()
    assert login(client, "ap-org", "j@ap.pk", "JPass123!").status_code == 200
    jn = client.get("/api/v1/notifications").json()["items"]
    assert any(n["type"] == "approval.decided" for n in jn)
