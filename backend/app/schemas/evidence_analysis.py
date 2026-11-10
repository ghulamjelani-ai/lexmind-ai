from __future__ import annotations

from pydantic import BaseModel


class EvidenceAnalysisOut(BaseModel):
    supporting: list[str]
    contradicting: list[str]
    missing: list[str]
    notes: str
    chunks_used: int
