from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: uuid.UUID
    type: str
    title: str
    body: str | None
    payload_json: dict
    read_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
