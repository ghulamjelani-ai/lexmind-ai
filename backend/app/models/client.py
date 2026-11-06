from __future__ import annotations

import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import GUID, Base, SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin


class Client(UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin, Base):
    """A chamber client. CNIC/government IDs are stored encrypted at rest."""

    __tablename__ = "clients"

    full_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    cnic_enc: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(String(512), nullable=True)
    assigned_lawyer_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)

    @property
    def has_cnic(self) -> bool:
        return bool(self.cnic_enc)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Client {self.full_name} org={self.organization_id}>"
