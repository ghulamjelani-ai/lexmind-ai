from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ConversationCreate(BaseModel):
    mode: str = "general"
    case_id: uuid.UUID | None = None
    title: str | None = Field(default=None, max_length=300)

    @field_validator("mode")
    @classmethod
    def _mode(cls, v):
        if v not in ("general", "case"):
            raise ValueError("mode must be 'general' or 'case'")
        return v


class ConversationOut(BaseModel):
    id: uuid.UUID
    mode: str
    case_id: uuid.UUID | None
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    citations_json: list
    created_at: datetime

    model_config = {"from_attributes": True}


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class AskResponse(BaseModel):
    message: MessageOut


class IngestRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    text: str = Field(min_length=1)
    source_type: str = "manual"
    case_id: uuid.UUID | None = None


class IngestResponse(BaseModel):
    kb_document_id: uuid.UUID
    chunks: int
