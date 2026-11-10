from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TaxQueryIn(BaseModel):
    # Any string is accepted; the server-side guard decides whether it reaches the
    # model, so an empty/invalid query returns a helpful message, not a 422 error.
    query: str = Field(default="", max_length=1000)


class TaxSourceOut(BaseModel):
    key: str
    name: str
    url: str
    kind: str
    note: str


class TaxAnswerOut(BaseModel):
    forwarded_to_ai: bool
    answer: str
    sources: list[TaxSourceOut] = []
    disclaimer: str
    model_used: str | None = None
    rejection_code: str | None = None
    examples: list[str] = []


class TaxReferenceOut(BaseModel):
    last_verified: str
    disclaimer: str
    filer_status: dict[str, Any]
    withholding_examples: list[dict[str, Any]]
    deadlines: list[dict[str, Any]]
    deadline_guidance: str
    ntn_registration: dict[str, Any]
    chamber_membership: dict[str, Any]
    sources: list[TaxSourceOut]
