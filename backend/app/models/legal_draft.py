from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import GUID, Base, TenantMixin, TimestampMixin, UUIDMixin


class LegalDraft(UUIDMixin, TimestampMixin, TenantMixin, Base):
    """An AI-generated legal document draft (bail application, legal notice, …).

    Always a DRAFT until a qualified lawyer approves it. Unverifiable specifics
    are left as explicit [PLACEHOLDER] markers rather than invented, and no
    citation is fabricated — the lawyer fills and verifies before use
    (docs/architecture/08, 09).
    """

    __tablename__ = "legal_drafts"

    case_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False
    )
    draft_type: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True, nullable=False)
    model_used: Mapped[str | None] = mapped_column(String(80), nullable=True)
    generated_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
