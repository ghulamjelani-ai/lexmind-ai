"""Reporting: scope-aware case summary statistics and CSV export.

Everything here is derived from the cases the caller is allowed to read, so a
user only ever sees figures for cases within their scope (docs/architecture/07).
"""

from __future__ import annotations

import csv
import io
from collections import Counter
from collections.abc import Iterator
from datetime import date

from sqlalchemy.orm import Session

from app.core.rbac import AuthContext
from app.services import case_service

_DORMANT = {"closed", "archived"}


def case_summary(db: Session, ctx: AuthContext, *, today: date | None = None) -> dict:
    today = today or date.today()
    cases = case_service.accessible_cases(db, ctx)

    by_status: Counter[str] = Counter()
    by_priority: Counter[str] = Counter()
    by_category: Counter[str] = Counter()
    upcoming_7d = 0
    overdue = 0
    for c in cases:
        by_status[c.status] += 1
        by_priority[c.priority] += 1
        by_category[c.category] += 1
        if c.next_hearing_date and c.status not in _DORMANT:
            days = (c.next_hearing_date - today).days
            if days < 0:
                overdue += 1
            elif days <= 7:
                upcoming_7d += 1

    active = sum(1 for c in cases if c.status not in _DORMANT)
    return {
        "total_cases": len(cases),
        "active_cases": active,
        "by_status": dict(by_status),
        "by_priority": dict(by_priority),
        "by_category": dict(by_category),
        "hearings_next_7_days": upcoming_7d,
        "overdue_hearings": overdue,
        "generated_on": today.isoformat(),
    }


_CSV_COLUMNS = [
    "id",
    "title",
    "case_number",
    "category",
    "status",
    "priority",
    "court_name",
    "filing_date",
    "next_hearing_date",
    "created_at",
]


def cases_csv(db: Session, ctx: AuthContext) -> Iterator[str]:
    """Yield the CSV export of accessible cases, one row at a time."""
    cases = case_service.accessible_cases(db, ctx)
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    def _flush() -> str:
        value = buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)
        return value

    writer.writerow(_CSV_COLUMNS)
    yield _flush()
    for c in cases:
        writer.writerow(
            [
                str(c.id),
                c.title,
                c.case_number or "",
                c.category,
                c.status,
                c.priority,
                c.court_name or "",
                c.filing_date.isoformat() if c.filing_date else "",
                c.next_hearing_date.isoformat() if c.next_hearing_date else "",
                c.created_at.isoformat() if c.created_at else "",
            ]
        )
        yield _flush()
