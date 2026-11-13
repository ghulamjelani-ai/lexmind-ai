from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class EmailVerification(UUIDMixin, TimestampMixin, Base):
    """A single-use, time-limited email OTP for pre-account flows (e.g. signup).

    This is a PRE-tenant table (no organization exists yet), so it is not
    tenant-scoped and is only accessed via the privileged connection. Only the
    hash of the code is stored; ``payload`` holds the pending registration data
    (org name/slug, owner name, already-hashed password)."""

    __tablename__ = "email_verifications"

    email: Mapped[str] = mapped_column(String(320), index=True, nullable=False)
    purpose: Mapped[str] = mapped_column(String(40), default="signup", nullable=False)
    code_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
