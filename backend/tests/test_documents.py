from app.core.rbac import JUNIOR_ADVOCATE
from tests.conftest import add_user, login, make_org


def _owner(client, db, slug):
    make_org(db, slug, owner_email=f"owner@{slug}.pk", password="OwnerPass123!")
    assert login(client, slug, f"owner@{slug}.pk", "OwnerPass123!").status_code == 200


def test_upload_download_and_version(client, db):
    _owner(client, db, "dc-org")
    r = client.post(
        "/api/v1/documents",
        files={"file": ("fir.txt", b"original FIR text", "text/plain")},
        data={"title": "FIR", "category": "fir"},
    )
    assert r.status_code == 201, r.text
    did = r.json()["id"]
    assert r.json()["size"] == len(b"original FIR text")
    assert r.json()["scan_status"] == "pending"
    assert r.json()["current_version"] == 1

    # Download returns the exact bytes.
    dl = client.get(f"/api/v1/documents/{did}/download")
    assert dl.status_code == 200
    assert dl.content == b"original FIR text"

    # New version bumps current_version and versions list has 2.
    v = client.post(
        f"/api/v1/documents/{did}/versions",
        files={"file": ("fir2.txt", b"amended FIR text", "text/plain")},
    )
    assert v.status_code == 200
    assert v.json()["current_version"] == 2
    assert len(client.get(f"/api/v1/documents/{did}/versions").json()) == 2
    assert client.get(f"/api/v1/documents/{did}/download").content == b"amended FIR text"


def test_upload_rejects_bad_category(client, db):
    _owner(client, db, "dc-cat")
    r = client.post(
        "/api/v1/documents",
        files={"file": ("f.txt", b"x", "text/plain")},
        data={"title": "T", "category": "nonsense"},
    )
    assert r.status_code == 400


def test_documents_require_permission(client, db):
    org, _ = make_org(db, "dc-authz", owner_email="owner@dca.pk", password="OwnerPass123!")
    add_user(db, org.id, "j@dca.pk", JUNIOR_ADVOCATE, password="JPass123!")
    # Junior has documents:upload/read/download (assigned scope) — can list.
    assert login(client, "dc-authz", "j@dca.pk", "JPass123!").status_code == 200
    assert client.get("/api/v1/documents").status_code == 200


def test_document_tenant_isolation(client, db):
    _owner(client, db, "dc-a")
    did = client.post(
        "/api/v1/documents",
        files={"file": ("a.txt", b"secret A", "text/plain")},
        data={"title": "A doc", "category": "other"},
    ).json()["id"]

    make_org(db, "dc-b", owner_email="owner@dcb.pk", password="PassB12345!")
    client.cookies.clear()
    assert login(client, "dc-b", "owner@dcb.pk", "PassB12345!").status_code == 200
    assert client.get(f"/api/v1/documents/{did}").status_code == 404
    assert client.get(f"/api/v1/documents/{did}/download").status_code == 404
    assert client.get("/api/v1/documents").json()["total"] == 0


def test_index_document_into_kb(client, db):
    _owner(client, db, "dc-index")
    cid = client.post(
        "/api/v1/cases", json={"title": "Indexed case", "category": "bail"}
    ).json()["id"]
    body = b"The accused was granted bail under section 497 CrPC."
    up = client.post(
        "/api/v1/documents",
        files={"file": ("brief.txt", body, "text/plain")},
        data={"title": "Brief", "category": "court_order", "case_id": cid},
    )
    did = up.json()["id"]

    r = client.post(f"/api/v1/documents/{did}/index")
    assert r.status_code == 200, r.text
    assert r.json()["chunks"] >= 1

    # The indexed text is now grounding for case-mode AI chat.
    conv = client.post(
        "/api/v1/ai/conversations", json={"mode": "case", "case_id": cid}
    ).json()["id"]
    msg = client.post(
        f"/api/v1/ai/conversations/{conv}/ask", json={"question": "Was bail granted?"}
    ).json()["message"]
    assert len(msg["citations_json"]) >= 1


def test_index_rejects_non_text(client, db):
    _owner(client, db, "dc-img")
    up = client.post(
        "/api/v1/documents",
        files={"file": ("scan.png", b"\x89PNG\r\n\x1a\n not real image text", "image/png")},
        data={"title": "Scan", "category": "other"},
    )
    did = up.json()["id"]
    r = client.post(f"/api/v1/documents/{did}/index")
    assert r.status_code == 400
