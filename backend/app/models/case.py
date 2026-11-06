from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import DEFAULT_CASE_PRIORITY, DEFAULT_CASE_STATUS
from app.db.base import GUID, Base, SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin


class Case(UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin, Base):
    """A legal case — the core record. See docs/architecture/03 (M2)."""

    __tablename__ = "cases"

    title: Mapped[str] = mapped_column(String(300), index=True, nullable=False)
    case_number: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)

    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    custom_category: Mapped[str | None] = mapped_column(String(120), nullable=True)

    client_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("clients.id", ondelete="SET NULL"), index=True, nullable=True
    )
    opposite_party: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)

    court_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    judge_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    police_station: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fir_number: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    district: Mapped[str | None] = mapped_column(String(120), nullable=True)
    province: Mapped[str | None] = mapped_column(String(120), nullable=True)

    status: Mapped[str] = mapped_column(
        String(40), default=DEFAULT_CASE_STATUS, index=True, nullable=False
    )
    priority: Mapped[str] = mapped_column(
        String(20), default=DEFAULT_CASE_PRIORITY, index=True, nullable=False
    )
    priority_overridden_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)

    filing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_hearing_date: Mapped[date | None] = mapped_column(Date, index=True, nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    legal_issues_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    assigned_lawyer_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), index=True, nullable=True
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), index=True, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Case {self.title!r} org={self.organization_id}>"


class CaseAssignment(UUIDMixin, TimestampMixin, TenantMixin, Base):
    """Which users work a case, and in what role (primary/supporting)."""

    __tablename__ = "case_assignments"
    __table_args__ = (
        UniqueConstraint("case_id", "user_id", name="uq_case_assignment"),
    )

    case_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role_on_case: Mapped[str] = mapped_column(String(20), default="supporting", nullable=False)
    assigned_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)


class CaseParty(UUIDMixin, TimestampMixin, TenantMixin, Base):
    """A party involved in a case (client, opposite, witness, …)."""

    __tablename__ = "case_parties"

    case_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    party_type: Mapped[str] = mapped_column(String(20), default="other", nullable=False)
    details_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class CaseEvent(UUIDMixin, TenantMixin, Base):
    """Append-only case timeline. Never updated or deleted."""

    __tablename__ = "case_events"

    case_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True, nullable=False
    )
