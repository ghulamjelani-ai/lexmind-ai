from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import DEFAULT_HEARING_STATUS
from app.db.base import GUID, Base, TenantMixin, TimestampMixin, UUIDMixin


class Hearing(UUIDMixin, TimestampMixin, TenantMixin, Base):
    """A court hearing for a case.

    A manually-entered hearing is `unconfirmed` until matched against an official
    source (confirmation_source) — the platform never claims a date is official
    just because someone typed it in (prompt §9).
    """

    __tablename__ = "hearings"

    case_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False
    )
    court_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default=DEFAULT_HEARING_STATUS, nullable=False)
    confirmation_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
