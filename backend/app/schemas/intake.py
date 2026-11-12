from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.core.validators import Phone


class LeadCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=320)
    phone: Phone = Field(default=None, max_length=50)
    opposing_party: str | None = Field(default=None, max_length=255)
    matter_type: str | None = Field(default=None, max_length=60)
    description: str | None = Field(default=None, max_length=4000)


class ConflictHitOut(BaseModel):
    severity: str
    kind: str
    reason: str
    match: str


class LeadOut(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str | None
    phone: str | None
    opposing_party: str | None
    matter_type: str | None
    description: str | None
    status: str
    conflict_level: str
    conflict_hits_json: list[ConflictHitOut]
    screened_at: datetime | None
    converted_case_id: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConvertIn(BaseModel):
    category: str = Field(default="other", max_length=50)
    override: bool = False
