from app.core.rbac import CLERK
from tests.conftest import add_user, login, make_org


def _owner(client, db, slug):
    make_org(db, slug, owner_email=f"owner@{slug}.pk", password="OwnerPass123!")
    assert login(client, slug, f"owner@{slug}.pk", "OwnerPass123!").status_code == 200


def test_official_sources(client, db):
    _owner(client, db, "lg-src")
    sources = client.get("/api/v1/legal/sources").json()
    keys = {s["key"] for s in sources}
    assert "pakistan_code" in keys
    assert all(s["authoritative"] for s in sources)


def test_provision_starts_pending_then_verify(client, db):
    _owner(client, db, "lg-prov")
    r = client.post(
        "/api/v1/legal/provisions",
        json={"law_name": "Pakistan Penal Code", "section": "302", "source_key": "pakistan_code"},
    )
    assert r.status_code == 201, r.text
    pid = r.json()["id"]
    # Never auto-verified — a citation is "pending" until a human/source confirms it.
    assert r.json()["verification_status"] == "pending"

    v = client.post(
        f"/api/v1/legal/provisions/{pid}/verify",
        json={"status": "verified", "source_url": "https://pakistancode.gov.pk/..."},
    )
    assert v.status_code == 200
    assert v.json()["verification_status"] == "verified"
    assert v.json()["retrieved_at"] is not None


def test_judgment_create_and_verify_treatment(client, db):
    _owner(client, db, "lg-judg")
    r = client.post(
        "/api/v1/legal/judgments",
        json={"title": "State vs X", "citation": "PLD 2020 SC 1", "court": "Supreme Court"},
    )
    assert r.status_code == 201, r.text
    jid = r.json()["id"]
    assert r.json()["verification_status"] == "pending"

    v = client.post(
        f"/api/v1/legal/judgments/{jid}/verify",
        json={"status": "verified", "treatment": "binding"},
    )
    assert v.status_code == 200
    assert v.json()["treatment"] == "binding"


def test_verify_rejects_bad_status(client, db):
    _owner(client, db, "lg-bad")
    pid = client.post(
        "/api/v1/legal/provisions", json={"law_name": "PPC"}
    ).json()["id"]
    bad = client.post(f"/api/v1/legal/provisions/{pid}/verify", json={"status": "totally-sure"})
    assert bad.status_code == 422


def test_legal_requires_permission(client, db):
    org, _ = make_org(db, "lg-authz", owner_email="owner@lga.pk", password="OwnerPass123!")
    add_user(db, org.id, "clerk@lga.pk", CLERK, password="ClerkPass123!")
    assert login(client, "lg-authz", "clerk@lga.pk", "ClerkPass123!").status_code == 200
    # Clerk lacks ai:research:run.
    assert client.get("/api/v1/legal/sources").status_code == 403
    assert client.get("/api/v1/legal/provisions").status_code == 403


def test_legal_tenant_isolation(client, db):
    _owner(client, db, "lg-a")
    pid = client.post("/api/v1/legal/provisions", json={"law_name": "Org A law"}).json()["id"]

    make_org(db, "lg-b", owner_email="owner@lgb.pk", password="PassB12345!")
    client.cookies.clear()
    assert login(client, "lg-b", "owner@lgb.pk", "PassB12345!").status_code == 200
    # Org B cannot see or verify org A's provision.
    cross = client.post(f"/api/v1/legal/provisions/{pid}/verify", json={"status": "verified"})
    assert cross.status_code == 404
    assert client.get("/api/v1/legal/provisions").json()["total"] == 0


def test_official_domains_include_official_sources():
    from app.integrations.legal_search import official_domains

    d = official_domains()
    assert "pakistancode.gov.pk" in d
    assert "supremecourt.gov.pk" in d


def test_research_without_search_is_ungrounded(client, db):
    _owner(client, db, "lg-res0")
    r = client.post("/api/v1/legal/research", json={"question": "What is section 497 CrPC?"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["answer"]) > 0
    assert body["references"] == []  # no official search configured in tests
    assert body["note"] is not None  # flagged as ungrounded — verify manually
    assert "pakistancode.gov.pk" in body["searched_domains"]


def test_research_grounded_in_official_results(db):
    # Inject official-source results (no network) and check grounding + citations.
    from app.ai import legal_research
    from app.integrations.legal_search import SearchResult
    from app.services.rbac_service import build_auth_context

    _, owner = make_org(db, "lg-res1")
    ctx = build_auth_context(db, owner)

    def fake_search(q, *, max_results=5):
        return [
            SearchResult(
                title="PPC Section 302",
                url="https://pakistancode.gov.pk/pdffiles/x.pdf",
                content="Section 302: punishment for qatl-i-amd.",
                domain="pakistancode.gov.pk",
            )
        ]

    res = legal_research.research(db, ctx, "Punishment for murder?", search_fn=fake_search)
    assert len(res.references) == 1
    assert res.references[0].domain == "pakistancode.gov.pk"
    assert res.references[0].verification_status == "pending"  # never auto-verified
    assert res.note is None
