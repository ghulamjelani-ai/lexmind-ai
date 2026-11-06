import uuid

from tests.conftest import login, make_org


def test_notifications_read_flow(client, db):
    org, owner = make_org(db, "nt-org", owner_email="owner@nt.pk", password="OwnerPass123!")

    # Generate a notification by requesting an approval addressed to the owner.
    assert login(client, "nt-org", "owner@nt.pk", "OwnerPass123!").status_code == 200
    client.post(
        "/api/v1/approvals",
        json={"target_type": "case", "target_id": str(uuid.uuid4()), "approver_id": str(owner.id)},
    )

    assert client.get("/api/v1/notifications/unread-count").json()["unread"] == 1
    items = client.get("/api/v1/notifications", params={"unread": True}).json()["items"]
    assert len(items) == 1
    nid = items[0]["id"]

    assert client.post(f"/api/v1/notifications/{nid}/read").status_code == 204
    assert client.get("/api/v1/notifications/unread-count").json()["unread"] == 0


def test_notifications_are_per_user(client, db):
    make_org(db, "nt-a", owner_email="owner@nta.pk", password="PassA12345!")
    make_org(db, "nt-b", owner_email="owner@ntb.pk", password="PassB12345!")
    # Org B owner has no notifications.
    assert login(client, "nt-b", "owner@ntb.pk", "PassB12345!").status_code == 200
    assert client.get("/api/v1/notifications/unread-count").json()["unread"] == 0
