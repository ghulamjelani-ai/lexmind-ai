from app.ai.tax_assistant import validate_query
from tests.conftest import login, make_org


def _owner(client, db, slug="tax-org"):
    make_org(db, slug, owner_email=f"owner@{slug}.pk", password="OwnerPass123!")
    assert login(client, slug, f"owner@{slug}.pk", "OwnerPass123!").status_code == 200


# --- pure guard (no model) ---------------------------------------------------
def test_guard_rejects_empty():
    v = validate_query("   ")
    assert not v.ok and v.code == "empty"


def test_guard_rejects_symbols_only():
    v = validate_query("@@@ 123 !!!")
    assert not v.ok and v.code in ("no_text", "too_short")


def test_guard_rejects_too_short():
    v = validate_query("tax")
    assert not v.ok and v.code in ("too_short", "off_topic")


def test_guard_rejects_off_topic_short():
    v = validate_query("hello there friend")
    assert not v.ok and v.code == "off_topic"


def test_guard_accepts_tax_question():
    assert validate_query("What is the difference between filer and non-filer?").ok
    assert validate_query("How do I register for an NTN on IRIS?").ok


# --- endpoint: guard path spends no AI call ----------------------------------
def test_ask_rejects_without_forwarding(client, db):
    _owner(client, db, "tax-guard")
    r = client.post("/api/v1/tax/ask", json={"query": "??"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["forwarded_to_ai"] is False
    assert body["rejection_code"]
    assert body["examples"]  # user is guided
    assert body["answer"]  # a helpful message, not a model answer


def test_ask_empty_query_is_graceful(client, db):
    _owner(client, db, "tax-empty")
    body = client.post("/api/v1/tax/ask", json={"query": ""}).json()
    assert body["forwarded_to_ai"] is False
    assert body["rejection_code"] == "empty"


def test_ask_valid_query_is_answered(client, db):
    _owner(client, db, "tax-ok")
    body = client.post(
        "/api/v1/tax/ask",
        json={"query": "What documents are needed for NTN registration on IRIS?"},
    ).json()
    assert body["forwarded_to_ai"] is True
    assert body["answer"]
    assert body["disclaimer"]
    assert any(s["key"] == "iris" for s in body["sources"])


# --- reference (static, no AI) -----------------------------------------------
def test_reference_has_sources_and_deadlines(client, db):
    _owner(client, db, "tax-ref")
    ref = client.get("/api/v1/tax/reference").json()
    assert ref["last_verified"]
    assert any(s["key"] == "iris" for s in ref["sources"])
    assert ref["deadlines"] and ref["ntn_registration"]["steps"]
    assert ref["chamber_membership"]["documents"]
