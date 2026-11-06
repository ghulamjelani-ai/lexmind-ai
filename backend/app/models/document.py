from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import DOC_SCAN_PENDING
from app.db.base import GUID, Base, SoftDeleteMixin, TenantMixin, TimestampMixin, UUIDMixin


class Document(UUIDMixin, TimestampMixin, TenantMixin, SoftDeleteMixin, Base):
    """A document stored in private object storage, referenced by storage_key.

    Bytes never live in the database; the API returns short-lived presigned URLs.
    Malware scanning (scan_status) and OCR land in later phases.
    """

    __tablename__ = "documents"

    case_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    category: Mapped[str] = mapped_column(String(40), default="other", index=True, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    mime: Mapped[str | None] = mapped_column(String(120), nullable=True)
    size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    scan_status: Mapped[str] = mapped_column(String(20), default=DOC_SCAN_PENDING, nullable=False)
    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), index=True, nullable=True)


class DocumentVersion(UUIDMixin, TimestampMixin, TenantMixin, Base):
    """An immutable version of a document (revision history)."""

    __tablename__ = "document_versions"

    document_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    mime: Mapped[str | None] = mapped_column(String(120), nullable=True)
    size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
