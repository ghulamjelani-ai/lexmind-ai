from __future__ import annotations

import uuid

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import GUID, Base, TenantMixin, TimestampMixin, UUIDMixin


class AiConversation(UUIDMixin, TimestampMixin, TenantMixin, Base):
    """A chatbot conversation. mode is 'general' or 'case' (bound to a case)."""

    __tablename__ = "ai_conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), index=True, nullable=False)
    mode: Mapped[str] = mapped_column(String(20), default="general", nullable=False)
    case_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(300), default="New conversation", nullable=False)


class AiMessage(UUIDMixin, TimestampMixin, TenantMixin, Base):
    """A message in a conversation. citations_json holds grounding references."""

    __tablename__ = "ai_messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("ai_conversations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user|assistant|system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # Each citation: {chunk_id, source_ref, quoted_text, verification_status}
    citations_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
