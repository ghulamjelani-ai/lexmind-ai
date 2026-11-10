from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import GUID, Base, TenantMixin, TimestampMixin, UUIDMixin


class Lead(UUIDMixin, TimestampMixin, TenantMixin, Base):
    """A prospective client / matter captured at intake.

    A lead is screened for conflicts of interest BEFORE it can become a case, and
    is converted into a client + case only after a lawyer approves it (the blueprint
    intake -> conflict-check -> approval -> matter workflow).
    """

    __tablename__ = "leads"

    full_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    opposing_party: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    matter_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="new", index=True, nullable=False)
    # Conflict screening outcome: pending | clear | review | block
    conflict_level: Mapped[str] = mapped_column(
        String(20), default="pending", index=True, nullable=False
    )
    conflict_hits_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    screened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    converted_case_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
