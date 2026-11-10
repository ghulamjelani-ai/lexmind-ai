from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class PriorityFactorOut(BaseModel):
    factor: str
    points: int
    reason: str


class PriorityScoreOut(BaseModel):
    case_id: str
    title: str
    score: int
    level: str
    factors: list[PriorityFactorOut]


class CaseAnalysisOut(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    report_json: dict
    status: str
    model_used: str | None
    generated_by: uuid.UUID | None
    approved_by: uuid.UUID | None
    approved_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
