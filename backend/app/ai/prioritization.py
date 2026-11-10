"""Explainable case prioritization.

A transparent, rule-based scorer — NOT a black-box model. Every case gets a
score that is the sum of named factors, each carrying the points it contributed
and a plain-language reason, so a lawyer can see exactly why a case ranks where
it does and overrule it with judgement (docs/architecture/07). Deterministic:
`today` is injectable so the ranking is reproducible and testable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.models.case import Case

_PRIORITY_POINTS = {"critical": 40, "high": 28, "medium": 15, "low": 5}
_DORMANT_STATUSES = {"closed", "archived"}


@dataclass
class PriorityFactor:
    factor: str
    points: int
    reason: str


@dataclass
class PriorityScore:
    case_id: str
    title: str
    score: int
    level: str  # critical | high | medium | low
    factors: list[PriorityFactor] = field(default_factory=list)


def _level(score: int) -> str:
    if score >= 60:
        return "critical"
    if score >= 40:
        return "high"
    if score >= 20:
        return "medium"
    return "low"


def _hearing_factor(case: Case, today: date) -> PriorityFactor | None:
    if case.next_hearing_date is None:
        return PriorityFactor("hearing", 0, "No hearing scheduled.")
    days = (case.next_hearing_date - today).days
    if days < 0:
        return PriorityFactor("hearing", 32, f"Hearing date passed {-days} day(s) ago.")
    if days == 0:
        return PriorityFactor("hearing", 35, "Hearing is today.")
    if days <= 3:
        return PriorityFactor("hearing", 30, f"Hearing in {days} day(s).")
    if days <= 7:
        return PriorityFactor("hearing", 20, f"Hearing in {days} days.")
    if days <= 14:
        return PriorityFactor("hearing", 10, f"Hearing in {days} days.")
    if days <= 30:
        return PriorityFactor("hearing", 5, f"Hearing in {days} days.")
    return PriorityFactor("hearing", 0, f"Hearing in {days} days (not imminent).")


def score_case(case: Case, *, today: date) -> PriorityScore:
    factors: list[PriorityFactor] = []

    # Dormant cases are pinned to the bottom with a single clear reason.
    if case.status in _DORMANT_STATUSES:
        factors.append(PriorityFactor("status", 0, f"Case is {case.status} — not active."))
        return PriorityScore(str(case.id), case.title, 0, "low", factors)

    prio = (case.priority or "medium").lower()
    factors.append(
        PriorityFactor("priority", _PRIORITY_POINTS.get(prio, 15), f"Priority is {prio}.")
    )

    hearing = _hearing_factor(case, today)
    if hearing is not None:
        factors.append(hearing)

    if case.status == "in_hearing":
        factors.append(PriorityFactor("status", 15, "Case is currently in hearing."))
    elif case.status == "under_investigation":
        factors.append(PriorityFactor("status", 8, "Case is under investigation."))

    score = max(0, sum(f.points for f in factors))
    return PriorityScore(str(case.id), case.title, score, _level(score), factors)


def rank(cases: list[Case], *, today: date) -> list[PriorityScore]:
    """Score and sort cases, most urgent first. Ties break by title for stability."""
    scored = [score_case(c, today=today) for c in cases]
    scored.sort(key=lambda s: (-s.score, s.title.lower()))
    return scored
