from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.legal_sources import DEFAULT_VERIFICATION_STATUS
from app.db.base import GUID, Base, TenantMixin, TimestampMixin, UUIDMixin


class LegalProvision(UUIDMixin, TimestampMixin, TenantMixin, Base):
    """A cached reference to a piece of legislation, with its verification state.

    This is a verification cache, NOT a source of truth: every row carries a
    source_url and a verification_status, and nothing is presented as verified
    unless it actually was (see docs/architecture/09).
    """

    __tablename__ = "legal_provisions"

    law_name: Mapped[str] = mapped_column(String(300), index=True, nullable=False)
    section: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_key: Mapped[str | None] = mapped_column(String(60), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    verification_status: Mapped[str] = mapped_column(
        String(20), default=DEFAULT_VERIFICATION_STATUS, index=True, nullable=False
    )
    amended_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)


class Judgment(UUIDMixin, TimestampMixin, TenantMixin, Base):
    """A cached reference to a court judgment, with its verification state."""

    __tablename__ = "judgments"

    title: Mapped[str] = mapped_column(String(400), index=True, nullable=False)
    citation: Mapped[str | None] = mapped_column(String(200), index=True, nullable=True)
    court: Mapped[str | None] = mapped_column(String(200), nullable=True)
    judgment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    verification_status: Mapped[str] = mapped_column(
        String(20), default=DEFAULT_VERIFICATION_STATUS, index=True, nullable=False
    )
    treatment: Mapped[str | None] = mapped_column(String(20), nullable=True)
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
