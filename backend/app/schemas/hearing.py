from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.core.constants import HEARING_STATUSES


class HearingCreate(BaseModel):
    scheduled_at: datetime
    court_name: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class HearingUpdate(BaseModel):
    scheduled_at: datetime | None = None
    court_name: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    status: str | None = None

    @field_validator("status")
    @classmethod
    def _status(cls, v):
        if v is not None and v not in HEARING_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(HEARING_STATUSES)}")
        return v


class HearingConfirm(BaseModel):
    confirmation_source: str = Field(min_length=1, max_length=255)


class HearingOut(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    court_name: str | None
    scheduled_at: datetime
    status: str
    confirmation_source: str | None
    notes: str | None

    model_config = {"from_attributes": True}


class CalendarItem(BaseModel):
    kind: str  # "hearing" | "task"
    id: uuid.UUID
    case_id: uuid.UUID | None
    title: str
    at: datetime
    status: str
