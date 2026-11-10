from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import GUID, Base, TenantMixin, TimestampMixin, UUIDMixin


class CaseAnalysis(UUIDMixin, TimestampMixin, TenantMixin, Base):
    """An AI-generated structured case analysis report.

    A DRAFT until a qualified lawyer approves it. The report never declares guilt
    or a final offence; every section is traceable and flags what needs lawyer
    verification (docs/architecture/05, 08).
    """

    __tablename__ = "case_analyses"

    case_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # report_json: {section_key: {"title": str, "content": str}}
    report_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True, nullable=False)
    model_used: Mapped[str | None] = mapped_column(String(80), nullable=True)
    generated_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
