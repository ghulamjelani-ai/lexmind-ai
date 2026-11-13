from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai import gateway, retrieval
from app.api.deps import get_tenant_db, require, require_not_restricted
from app.core.rbac import AuthContext
from app.models.knowledge import KbChunk
from app.schemas.ai import (
    AskRequest,
    AskResponse,
    ConversationCreate,
    ConversationOut,
    IngestRequest,
    IngestResponse,
    MessageOut,
)
from app.services import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/conversations", response_model=ConversationOut, status_code=201)
def create_conversation(
    body: ConversationCreate,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("ai:research:run")),
) -> ConversationOut:
    conv = ai_service.create_conversation(db, ctx, body)
    db.commit()
    db.refresh(conv)
    return ConversationOut.model_validate(conv)


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("ai:research:run")),
) -> list[ConversationOut]:
    return [ConversationOut.model_validate(c) for c in ai_service.list_conversations(db, ctx)]


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageOut])
def list_messages(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("ai:research:run")),
) -> list[MessageOut]:
    conv = ai_service.get_conversation(db, ctx, conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return [MessageOut.model_validate(m) for m in ai_service.list_messages(db, conv)]


@router.post("/conversations/{conversation_id}/ask", response_model=AskResponse)
def ask(
    conversation_id: uuid.UUID,
    body: AskRequest,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("ai:research:run")),
) -> AskResponse:
    conv = ai_service.get_conversation(db, ctx, conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    try:
        msg = ai_service.ask(db, ctx, conv, body.question)
    except gateway.AiAuthorizationError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    db.commit()
    db.refresh(msg)
    return AskResponse(message=MessageOut.model_validate(msg))


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


@router.post(
    "/conversations/{conversation_id}/ask/stream",
    dependencies=[Depends(require_not_restricted)],
)
def ask_stream(
    conversation_id: uuid.UUID,
    body: AskRequest,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("ai:research:run")),
) -> StreamingResponse:
    """Stream the assistant's reply as Server-Sent Events.

    Emits `{"delta": "..."}` events as tokens arrive, then a final
    `{"done": true, "message_id": ..., "citations": [...]}` event.
    """
    conv = ai_service.get_conversation(db, ctx, conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Authorize + retrieve eagerly so access errors become a clean 403.
    try:
        citations, stream = ai_service.begin_stream(db, ctx, conv, body.question)
    except gateway.AiAuthorizationError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    def event_stream():
        parts: list[str] = []
        try:
            for delta in stream:
                parts.append(delta)
                yield _sse({"delta": delta})
        except Exception as exc:  # provider error mid-stream
            yield _sse({"error": str(exc)})
        msg = ai_service.finish_stream(db, ctx, conv, "".join(parts), citations)
        yield _sse(
            {"done": True, "message_id": str(msg.id), "citations": citations}
        )

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/knowledge/ingest", response_model=IngestResponse, status_code=201)
def ingest_knowledge(
    body: IngestRequest,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("documents:upload")),
) -> IngestResponse:
    doc = retrieval.ingest(
        db, ctx,
        title=body.title, text=body.text, source_type=body.source_type, case_id=body.case_id,
    )
    n = db.scalar(
        select(func.count()).select_from(KbChunk).where(KbChunk.kb_document_id == doc.id)
    ) or 0
    db.commit()
    return IngestResponse(kb_document_id=doc.id, chunks=n)
