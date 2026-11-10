from datetime import date, timedelta

from app.ai.prioritization import rank, score_case
from tests.conftest import login, make_org

TODAY = date(2026, 6, 1)


class _FakeCase:
    """Lightweight stand-in so the pure scorer can be tested without the DB."""

    def __init__(self, title, *, priority="medium", status="open", next_hearing_date=None):
        self.id = title
        self.title = title
        self.priority = priority
        self.status = status
        self.next_hearing_date = next_hearing_date


def test_imminent_hearing_outranks_far_hearing():
    soon = _FakeCase("soon", next_hearing_date=TODAY + timedelta(days=1))
    later = _FakeCase("later", next_hearing_date=TODAY + timedelta(days=40))
    assert score_case(soon, today=TODAY).score > score_case(later, today=TODAY).score


def test_factors_explain_the_score():
    s = score_case(
        _FakeCase("c", priority="high", next_hearing_date=TODAY + timedelta(days=2)), today=TODAY
    )
    names = {f.factor for f in s.factors}
    assert "priority" in names and "hearing" in names
    # Score equals the sum of its factor points — fully explainable.
    assert s.score == sum(f.points for f in s.factors)
    assert all(f.reason for f in s.factors)


def test_passed_hearing_is_flagged():
    s = score_case(_FakeCase("overdue", next_hearing_date=TODAY - timedelta(days=5)), today=TODAY)
    reasons = " ".join(f.reason for f in s.factors)
    assert "passed" in reasons.lower()


def test_dormant_case_pinned_to_bottom():
    s = score_case(_FakeCase("closed one", status="closed", priority="critical"), today=TODAY)
    assert s.score == 0 and s.level == "low"


def test_rank_orders_desc_and_is_stable():
    cases = [
        _FakeCase("low far", priority="low", next_hearing_date=TODAY + timedelta(days=60)),
        _FakeCase("critical today", priority="critical", next_hearing_date=TODAY),
    ]
    ranked = rank(cases, today=TODAY)
    assert ranked[0].title == "critical today"


# --- endpoint ----------------------------------------------------------------
def _owner(client, db, slug):
    make_org(db, slug, owner_email=f"owner@{slug}.pk", password="OwnerPass123!")
    assert login(client, slug, f"owner@{slug}.pk", "OwnerPass123!").status_code == 200


def test_priority_queue_endpoint_ranks_and_explains(client, db):
    _owner(client, db, "pq")
    near = (date.today() + timedelta(days=1)).isoformat()
    far = (date.today() + timedelta(days=90)).isoformat()
    client.post("/api/v1/cases", json={"title": "Urgent", "category": "murder",
                                       "priority": "critical", "next_hearing_date": near})
    client.post("/api/v1/cases", json={"title": "Relaxed", "category": "civil",
                                       "priority": "low", "next_hearing_date": far})
    r = client.get("/api/v1/cases/priority-queue")
    assert r.status_code == 200, r.text
    rows = r.json()
    assert [row["title"] for row in rows][:2] == ["Urgent", "Relaxed"]
    assert rows[0]["factors"] and rows[0]["score"] == sum(f["points"] for f in rows[0]["factors"])


def test_priority_queue_excludes_closed(client, db):
    _owner(client, db, "pq-closed")
    cid = client.post("/api/v1/cases", json={"title": "Done", "category": "civil"}).json()["id"]
    client.patch(f"/api/v1/cases/{cid}", json={"status": "closed"})
    titles = [row["title"] for row in client.get("/api/v1/cases/priority-queue").json()]
    assert "Done" not in titles
