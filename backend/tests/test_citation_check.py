from app.ai.citation_check import check_text, classify
from tests.conftest import login, make_org

PPC = "The Pakistan Penal Code"


# --- pure matcher ------------------------------------------------------------
def test_check_text_finds_section_as_whole_token():
    assert check_text("302", "Whoever commits murder shall be punished under Section 302.") == (
        True,
        False,
    )
    # 302 must not match inside 3029
    assert check_text("302", "see paragraph 3029 of the manual")[0] is False


def test_check_text_handles_letter_suffix():
    assert check_text("302-A", "Section 302-A deals with...")[0] is True
    assert check_text("302A", "punishable under section 302-A of the code")[0] is True


def test_check_text_flags_amendment_hint():
    found, amended = check_text("500", "Section 500 was omitted by the amendment act.")
    assert found is True and amended is True


# --- classifier --------------------------------------------------------------
def test_classify_verified_when_found_clean():
    v = classify("302", [("https://pakistancode.gov.pk/x", "Punishment under Section 302 is...")])
    assert v.status == "verified"
    assert v.matched_url.endswith("/x")


def test_classify_conflicting_on_amendment():
    v = classify("500", [("https://pakistancode.gov.pk/y", "Section 500 has been repealed.")])
    assert v.status == "conflicting"


def test_classify_unverified_when_absent():
    v = classify("999", [("https://lhc.gov.pk/z", "Unrelated official content without it.")])
    assert v.status == "unverified"


def test_classify_pending_without_sources():
    assert classify("302", []).status == "pending"


# --- endpoint (no search provider configured in tests) -----------------------
def test_auto_verify_endpoint_pending_without_search(client, db):
    make_org(db, "cc-org", owner_email="owner@cc.pk", password="OwnerPass123!")
    assert login(client, "cc-org", "owner@cc.pk", "OwnerPass123!").status_code == 200
    pid = client.post(
        "/api/v1/legal/provisions", json={"law_name": PPC, "section": "302"}
    ).json()["id"]
    r = client.post(f"/api/v1/legal/provisions/{pid}/auto-verify")
    assert r.status_code == 200, r.text
    body = r.json()
    # No official search configured -> cannot confirm -> stays pending, never verified.
    assert body["status"] == "pending"
    assert body["provision"]["verification_status"] == "pending"
    assert body["note"]
