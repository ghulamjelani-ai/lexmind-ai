from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from app.core.constants import (
    CASE_CATEGORIES,
    CASE_PRIORITIES,
    CASE_ROLES,
    CASE_STATUSES,
    DEFAULT_CASE_PRIORITY,
    DEFAULT_CASE_STATUS,
    PARTY_TYPES,
)


def _one_of(field: str, allowed: list[str]):
    def validator(cls, v):  # noqa: N805
        if v is not None and v not in allowed:
            raise ValueError(f"{field} must be one of: {', '.join(allowed)}")
        return v

    return validator


class CaseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    category: str
    custom_category: str | None = Field(default=None, max_length=120)
    client_id: uuid.UUID | None = None
    opposite_party: str | None = Field(default=None, max_length=255)
    case_number: str | None = Field(default=None, max_length=120)
    court_name: str | None = Field(default=None, max_length=255)
    judge_name: str | None = Field(default=None, max_length=255)
    police_station: str | None = Field(default=None, max_length=255)
    fir_number: str | None = Field(default=None, max_length=120)
    district: str | None = Field(default=None, max_length=120)
    province: str | None = Field(default=None, max_length=120)
    status: str = DEFAULT_CASE_STATUS
    priority: str = DEFAULT_CASE_PRIORITY
    filing_date: date | None = None
    next_hearing_date: date | None = None
    description: str | None = None
    legal_issues: list[str] = Field(default_factory=list)

    _v_cat = field_validator("category")(_one_of("category", CASE_CATEGORIES))
    _v_status = field_validator("status")(_one_of("status", CASE_STATUSES))
    _v_prio = field_validator("priority")(_one_of("priority", CASE_PRIORITIES))


class CaseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    category: str | None = None
    custom_category: str | None = Field(default=None, max_length=120)
    client_id: uuid.UUID | None = None
    opposite_party: str | None = Field(default=None, max_length=255)
    case_number: str | None = Field(default=None, max_length=120)
    court_name: str | None = Field(default=None, max_length=255)
    judge_name: str | None = Field(default=None, max_length=255)
    police_station: str | None = Field(default=None, max_length=255)
    fir_number: str | None = Field(default=None, max_length=120)
    district: str | None = Field(default=None, max_length=120)
    province: str | None = Field(default=None, max_length=120)
    status: str | None = None
    priority: str | None = None
    filing_date: date | None = None
    next_hearing_date: date | None = None
    description: str | None = None
    legal_issues: list[str] | None = None

    _v_cat = field_validator("category")(_one_of("category", CASE_CATEGORIES))
    _v_status = field_validator("status")(_one_of("status", CASE_STATUSES))
    _v_prio = field_validator("priority")(_one_of("priority", CASE_PRIORITIES))


class CaseOut(BaseModel):
    id: uuid.UUID
    title: str
    case_number: str | None
    category: str
    custom_category: str | None
    client_id: uuid.UUID | None
    opposite_party: str | None
    court_name: str | None
    judge_name: str | None
    police_station: str | None
    fir_number: str | None
    district: str | None
    province: str | None
    status: str
    priority: str
    filing_date: date | None
    next_hearing_date: date | None
    description: str | None
    legal_issues_json: list
    assigned_lawyer_id: uuid.UUID | None
    created_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssignmentIn(BaseModel):
    user_id: uuid.UUID
    role_on_case: str = "supporting"

    _v_role = field_validator("role_on_case")(_one_of("role_on_case", CASE_ROLES))


class AssignmentOut(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    user_id: uuid.UUID
    role_on_case: str

    model_config = {"from_attributes": True}


class PartyIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    party_type: str = "other"
    details: dict = Field(default_factory=dict)

    _v_type = field_validator("party_type")(_one_of("party_type", PARTY_TYPES))


class PartyOut(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    name: str
    party_type: str
    details_json: dict

    model_config = {"from_attributes": True}


class NoteIn(BaseModel):
    note: str = Field(min_length=1, max_length=5000)


class EventOut(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    event_type: str
    actor_id: uuid.UUID | None
    payload_json: dict
    occurred_at: datetime

    model_config = {"from_attributes": True}
