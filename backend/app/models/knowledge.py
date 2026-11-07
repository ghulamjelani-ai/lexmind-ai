from __future__ import annotations

import uuid

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import GUID, Base, TenantMixin, TimestampMixin, UUIDMixin


class KbDocument(UUIDMixin, TimestampMixin, TenantMixin, Base):
    """A source ingested into the knowledge base for retrieval (RAG).

    access_metadata_json carries the authorization scope (e.g. {"case_id": ...})
    so retrieval can be filtered to what the caller may see.
    """

    __tablename__ = "kb_documents"

    # document | manual | legislation
    source_type: Mapped[str] = mapped_column(String(40), nullable=False)
    source_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    case_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), index=True, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="indexed", nullable=False)
    access_metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)


class KbChunk(UUIDMixin, TimestampMixin, TenantMixin, Base):
    """A chunk of a KB document with its embedding.

    The embedding is stored as JSON for portability (SQLite tests + Postgres).
    The production optimization is a native pgvector column + ANN index — a
    swap-in that does not change the retrieval authorization logic.
    """

    __tablename__ = "kb_chunks"

    kb_document_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("kb_documents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), index=True, nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
