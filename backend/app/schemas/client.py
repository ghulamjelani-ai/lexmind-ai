from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.core.validators import Cnic, OptionalEmail, Phone


class ClientCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    cnic: Cnic = Field(default=None, max_length=32)
    email: OptionalEmail = None
    phone: Phone = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=512)
    assigned_lawyer_id: uuid.UUID | None = None


class ClientUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    cnic: Cnic = Field(default=None, max_length=32)
    email: OptionalEmail = None
    phone: Phone = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=512)
    assigned_lawyer_id: uuid.UUID | None = None


class ClientOut(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    assigned_lawyer_id: uuid.UUID | None = None
    has_cnic: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class ConflictMatch(BaseModel):
    kind: str  # "existing_client" | "opposing_party"
    reference_id: uuid.UUID
    label: str


class ConflictResult(BaseModel):
    name: str
    has_conflict: bool
    matches: list[ConflictMatch]
