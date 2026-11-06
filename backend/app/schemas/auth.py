from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    org_slug: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_client: bool
    organization_id: uuid.UUID
    status: str

    model_config = {"from_attributes": True}


class MeOut(BaseModel):
    user: UserOut
    # permission code -> list of granted scopes
    permissions: dict[str, list[str]]


class OrgRegisterRequest(BaseModel):
    org_name: str = Field(min_length=1, max_length=255)
    org_slug: str = Field(min_length=2, max_length=120, pattern=r"^[a-z0-9][a-z0-9-]*$")
    owner_name: str = Field(min_length=1, max_length=255)
    owner_email: EmailStr
    owner_password: str = Field(min_length=8, max_length=256)


class OrgOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str

    model_config = {"from_attributes": True}


class UserCreateRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=256)
    role: str = Field(min_length=1, max_length=100)
    is_client: bool = False


class RoleOut(BaseModel):
    id: uuid.UUID
    name: str
    is_system: bool

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    message: str
