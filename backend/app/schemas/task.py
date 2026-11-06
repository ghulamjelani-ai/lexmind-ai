from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.core.constants import TASK_STATUSES


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    description: str | None = None
    case_id: uuid.UUID | None = None
    assignee_id: uuid.UUID | None = None
    due_at: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = None
    assignee_id: uuid.UUID | None = None
    due_at: datetime | None = None
    status: str | None = None

    @field_validator("status")
    @classmethod
    def _status(cls, v):
        if v is not None and v not in TASK_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(TASK_STATUSES)}")
        return v


class TaskOut(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID | None
    title: str
    description: str | None
    assignee_id: uuid.UUID | None
    due_at: datetime | None
    status: str
    created_by: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}
