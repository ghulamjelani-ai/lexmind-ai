"""Chatbot conversations and messages, on top of the ai_gateway."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai import gateway
from app.core.rbac import AuthContext
from app.models.ai import AiConversation, AiMessage
from app.schemas.ai import ConversationCreate


def create_conversation(db: Session, ctx: AuthContext, data: ConversationCreate) -> AiConversation:
    conv = AiConversation(
        organization_id=ctx.organization_id,
        user_id=ctx.user_id,
        mode=data.mode,
        case_id=data.case_id if data.mode == "case" else None,
        title=data.title or "New conversation",
    )
    db.add(conv)
    db.flush()
    return conv


def get_conversation(
    db: Session, ctx: AuthContext, conversation_id: uuid.UUID
) -> AiConversation | None:
    # A conversation is private to its owner.
    return db.scalar(
        select(AiConversation).where(
            AiConversation.id == conversation_id,
            AiConversation.organization_id == ctx.organization_id,
            AiConversation.user_id == ctx.user_id,
        )
    )


def list_conversations(db: Session, ctx: AuthContext) -> list[AiConversation]:
    return list(
        db.scalars(
            select(AiConversation)
            .where(
                AiConversation.organization_id == ctx.organization_id,
                AiConversation.user_id == ctx.user_id,
            )
            .order_by(AiConversation.created_at.desc())
        ).all()
    )


def list_messages(db: Session, conv: AiConversation) -> list[AiMessage]:
    return list(
        db.scalars(
            select(AiMessage)
            .where(AiMessage.conversation_id == conv.id)
            .order_by(AiMessage.created_at)
        ).all()
    )


def _count(db: Session, conv: AiConversation) -> int:
    return db.scalar(
        select(func.count()).select_from(AiMessage).where(AiMessage.conversation_id == conv.id)
    ) or 0


def ask(db: Session, ctx: AuthContext, conv: AiConversation, question: str) -> AiMessage:
    # Persist the user's message.
    db.add(
        AiMessage(
            organization_id=ctx.organization_id,
            conversation_id=conv.id,
            role="user",
            content=question,
        )
    )
    # Name the conversation after its first question.
    if _count(db, conv) == 0:
        conv.title = question[:60]
    db.flush()

    answer = gateway.ask(db, ctx, question=question, mode=conv.mode, case_id=conv.case_id)

    msg = AiMessage(
        organization_id=ctx.organization_id,
        conversation_id=conv.id,
        role="assistant",
        content=answer.content,
        citations_json=answer.citations,
    )
    db.add(msg)
    db.flush()
    return msg


def begin_stream(db: Session, ctx: AuthContext, conv: AiConversation, question: str):
    """Persist the user's message and start the AI stream. Authorization and
    retrieval happen here (eagerly), so an AiAuthorizationError raises before any
    streaming. Returns (citations, delta_iterator)."""
    db.add(
        AiMessage(
            organization_id=ctx.organization_id,
            conversation_id=conv.id,
            role="user",
            content=question,
        )
    )
    if _count(db, conv) == 0:
        conv.title = question[:60]
    db.flush()

    citations, stream = gateway.ask_stream(
        db, ctx, question=question, mode=conv.mode, case_id=conv.case_id
    )
    db.commit()  # persist the user message + audit before streaming begins
    return citations, stream


def finish_stream(
    db: Session, ctx: AuthContext, conv: AiConversation, content: str, citations: list[dict]
) -> AiMessage:
    """Persist the fully-streamed assistant message."""
    msg = AiMessage(
        organization_id=ctx.organization_id,
        conversation_id=conv.id,
        role="assistant",
        content=content,
        citations_json=citations,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
