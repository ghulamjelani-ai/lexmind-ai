from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.core.constants import APPROVAL_TARGETS


class ApprovalCreate(BaseModel):
    target_type: str
    target_id: uuid.UUID
    approver_id: uuid.UUID | None = None
    comment: str | None = None

    @field_validator("target_type")
    @classmethod
    def _target(cls, v):
        if v not in APPROVAL_TARGETS:
            raise ValueError(f"target_type must be one of: {', '.join(APPROVAL_TARGETS)}")
        return v


class ApprovalDecision(BaseModel):
    approve: bool
    comment: str | None = Field(default=None, max_length=2000)


class ApprovalOut(BaseModel):
    id: uuid.UUID
    target_type: str
    target_id: uuid.UUID
    status: str
    requested_by: uuid.UUID | None
    approver_id: uuid.UUID | None
    comment: str | None
    decided_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
