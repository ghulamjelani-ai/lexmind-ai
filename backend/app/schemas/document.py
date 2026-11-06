from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID | None
    title: str
    category: str
    mime: str | None
    size: int
    checksum: str | None
    scan_status: str
    current_version: int
    created_by: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentVersionOut(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    version_no: int
    mime: str | None
    size: int
    checksum: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
