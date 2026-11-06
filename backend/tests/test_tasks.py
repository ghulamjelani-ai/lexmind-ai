from app.core.rbac import JUNIOR_ADVOCATE
from tests.conftest import add_user, login, make_org


def test_task_crud_and_personal_scope(client, db):
    org, _ = make_org(db, "tk-org", owner_email="owner@tk.pk", password="OwnerPass123!")
    add_user(db, org.id, "j1@tk.pk", JUNIOR_ADVOCATE, password="J1Pass123!")

    # Junior 1 creates a task (defaults assignee to self).
    assert login(client, "tk-org", "j1@tk.pk", "J1Pass123!").status_code == 200
    r = client.post("/api/v1/tasks", json={"title": "Draft bail application"})
    assert r.status_code == 201, r.text
    tid = r.json()["id"]
    assert client.get("/api/v1/tasks").json()["total"] == 1

    # Update status.
    assert client.patch(f"/api/v1/tasks/{tid}", json={"status": "done"}).status_code == 200
    assert client.get(f"/api/v1/tasks/{tid}").json()["status"] == "done"


def test_owner_sees_all_tasks(client, db):
    org, _ = make_org(db, "tk-all", owner_email="owner@tka.pk", password="OwnerPass123!")
    add_user(db, org.id, "j@tka.pk", JUNIOR_ADVOCATE, password="JPass123!")

    assert login(client, "tk-all", "j@tka.pk", "JPass123!").status_code == 200
    client.post("/api/v1/tasks", json={"title": "Junior task"})

    client.cookies.clear()
    assert login(client, "tk-all", "owner@tka.pk", "OwnerPass123!").status_code == 200
    # Owner has tasks:create at scope all -> sees the junior's task.
    assert client.get("/api/v1/tasks").json()["total"] >= 1


def test_task_tenant_isolation(client, db):
    make_org(db, "tk-a", owner_email="owner@tk2a.pk", password="PassA12345!")
    make_org(db, "tk-b", owner_email="owner@tk2b.pk", password="PassB12345!")
    assert login(client, "tk-a", "owner@tk2a.pk", "PassA12345!").status_code == 200
    client.post("/api/v1/tasks", json={"title": "A task"})

    client.cookies.clear()
    assert login(client, "tk-b", "owner@tk2b.pk", "PassB12345!").status_code == 200
    assert client.get("/api/v1/tasks").json()["total"] == 0
