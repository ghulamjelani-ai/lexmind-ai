from datetime import date, timedelta

from app.core.rbac import CLIENT
from tests.conftest import add_user, login, make_org


def _owner(client, db, slug):
    make_org(db, slug, owner_email=f"owner@{slug}.pk", password="OwnerPass123!")
    assert login(client, slug, f"owner@{slug}.pk", "OwnerPass123!").status_code == 200


def test_summary_counts_by_dimension(client, db):
    _owner(client, db, "rep")
    near = (date.today() + timedelta(days=3)).isoformat()
    client.post("/api/v1/cases", json={"title": "A", "category": "murder",
                                        "priority": "critical", "next_hearing_date": near})
    client.post("/api/v1/cases", json={"title": "B", "category": "civil", "priority": "low"})
    s = client.get("/api/v1/reports/summary").json()
    assert s["total_cases"] == 2
    assert s["by_priority"].get("critical") == 1
    assert s["by_category"].get("murder") == 1
    assert s["hearings_next_7_days"] == 1


def test_overdue_hearing_counted(client, db):
    _owner(client, db, "rep-od")
    past = (date.today() - timedelta(days=2)).isoformat()
    client.post("/api/v1/cases", json={"title": "Late", "category": "civil",
                                        "next_hearing_date": past})
    assert client.get("/api/v1/reports/summary").json()["overdue_hearings"] == 1


def test_csv_export_has_header_and_rows(client, db):
    _owner(client, db, "rep-csv")
    client.post("/api/v1/cases", json={"title": "Exported", "category": "theft"})
    r = client.get("/api/v1/reports/cases.csv")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    lines = [ln for ln in r.text.splitlines() if ln.strip()]
    assert lines[0].startswith("id,title,case_number")
    assert any("Exported" in ln for ln in lines[1:])


def test_summary_requires_analytics_permission(client, db):
    org, _ = make_org(db, "rep-perm", owner_email="owner@rp.pk", password="OwnerPass123!")
    add_user(db, org.id, "client@rp.pk", CLIENT, password="ClientP1!")
    assert login(client, "rep-perm", "client@rp.pk", "ClientP1!").status_code == 200
    assert client.get("/api/v1/reports/summary").status_code == 403


def test_summary_tenant_isolation(client, db):
    _owner(client, db, "rep-a")
    client.post("/api/v1/cases", json={"title": "A-only", "category": "civil"})
    make_org(db, "rep-b", owner_email="owner@rb.pk", password="PassB12345!")
    client.cookies.clear()
    assert login(client, "rep-b", "owner@rb.pk", "PassB12345!").status_code == 200
    assert client.get("/api/v1/reports/summary").json()["total_cases"] == 0
