from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import GUID, Base, TenantMixin, TimestampMixin, UUIDMixin


class Approval(UUIDMixin, TimestampMixin, TenantMixin, Base):
    """A pending approval for a document, report, or record change.

    target_type + target_id point at the thing needing sign-off; kept generic so
    new approvable types don't require schema changes.
    """

    __tablename__ = "approvals"

    target_type: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(GUID(), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True, nullable=False)
    requested_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    approver_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
