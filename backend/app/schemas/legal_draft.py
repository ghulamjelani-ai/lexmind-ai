from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DraftCreate(BaseModel):
    draft_type: str = Field(min_length=1, max_length=60)
    title: str = Field(min_length=1, max_length=300)
    instructions: str | None = Field(default=None, max_length=4000)


class LegalDraftOut(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    draft_type: str
    title: str
    instructions: str | None
    content: str
    status: str
    model_used: str | None
    generated_by: uuid.UUID | None
    approved_by: uuid.UUID | None
    approved_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
