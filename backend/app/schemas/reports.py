from __future__ import annotations

from pydantic import BaseModel


class CaseSummaryOut(BaseModel):
    total_cases: int
    active_cases: int
    by_status: dict[str, int]
    by_priority: dict[str, int]
    by_category: dict[str, int]
    hearings_next_7_days: int
    overdue_hearings: int
    generated_on: str
