from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import DEFAULT_TASK_STATUS
from app.db.base import GUID, Base, TenantMixin, TimestampMixin, UUIDMixin


class Task(UUIDMixin, TimestampMixin, TenantMixin, Base):
    """A unit of work, optionally tied to a case and assigned to a user."""

    __tablename__ = "tasks"

    case_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), index=True, nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), index=True, nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), default=DEFAULT_TASK_STATUS, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), index=True, nullable=True)
