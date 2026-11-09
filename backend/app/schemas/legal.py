from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from app.core.legal_sources import TREATMENTS, VERIFICATION_STATUSES


class SourceOut(BaseModel):
    key: str
    name: str
    url: str
    tier: str
    jurisdiction: str
    authoritative: bool


class ProvisionCreate(BaseModel):
    law_name: str = Field(min_length=1, max_length=300)
    section: str | None = Field(default=None, max_length=120)
    text: str | None = None
    source_key: str | None = Field(default=None, max_length=60)
    source_url: str | None = Field(default=None, max_length=1000)


class ProvisionOut(BaseModel):
    id: uuid.UUID
    law_name: str
    section: str | None
    text: str | None
    source_key: str | None
    source_url: str | None
    verification_status: str
    amended_flag: bool
    retrieved_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JudgmentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=400)
    citation: str | None = Field(default=None, max_length=200)
    court: str | None = Field(default=None, max_length=200)
    judgment_date: date | None = None
    source_url: str | None = Field(default=None, max_length=1000)


class JudgmentOut(BaseModel):
    id: uuid.UUID
    title: str
    citation: str | None
    court: str | None
    judgment_date: date | None
    source_url: str | None
    verification_status: str
    treatment: str | None
    retrieved_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class VerifyRequest(BaseModel):
    status: str
    source_url: str | None = Field(default=None, max_length=1000)
    treatment: str | None = None

    @field_validator("status")
    @classmethod
    def _status(cls, v):
        if v not in VERIFICATION_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(VERIFICATION_STATUSES)}")
        return v

    @field_validator("treatment")
    @classmethod
    def _treatment(cls, v):
        if v is not None and v not in TREATMENTS:
            raise ValueError(f"treatment must be one of: {', '.join(TREATMENTS)}")
        return v
