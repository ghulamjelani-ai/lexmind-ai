"""Legal drafting: generate a draft, list, fetch, and approve it (the human
gate — a draft is never usable until a qualified lawyer approves it)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import drafting
from app.core.rbac import AuthContext
from app.models.case import Case, CaseEvent
from app.models.legal_draft import LegalDraft


def generate(
    db: Session,
    ctx: AuthContext,
    case: Case,
    *,
    draft_type: str,
    title: str,
    instructions: str | None,
) -> LegalDraft:
    result = drafting.draft(db, ctx, case, draft_type=draft_type, instructions=instructions)
    draft_row = LegalDraft(
        organization_id=ctx.organization_id,
        case_id=case.id,
        draft_type=draft_type,
        title=title,
        instructions=instructions,
        content=result.content,
        status="draft",
        model_used=result.model_used,
        generated_by=ctx.user_id,
    )
    db.add(draft_row)
    db.flush()
    db.add(
        CaseEvent(
            organization_id=ctx.organization_id,
            case_id=case.id,
            event_type="draft_generated",
            actor_id=ctx.user_id,
            payload_json={
                "draft_id": str(draft_row.id),
                "draft_type": draft_type,
                "chunks": result.chunks_used,
            },
        )
    )
    db.flush()
    return draft_row


def list_for_case(db: Session, case: Case) -> list[LegalDraft]:
    return list(
        db.scalars(
            select(LegalDraft)
            .where(LegalDraft.case_id == case.id)
            .order_by(LegalDraft.created_at.desc())
        ).all()
    )


def get(db: Session, ctx: AuthContext, draft_id: uuid.UUID) -> LegalDraft | None:
    return db.scalar(
        select(LegalDraft).where(
            LegalDraft.id == draft_id,
            LegalDraft.organization_id == ctx.organization_id,
        )
    )


def approve(db: Session, ctx: AuthContext, draft_row: LegalDraft) -> LegalDraft:
    draft_row.status = "approved"
    draft_row.approved_by = ctx.user_id
    draft_row.approved_at = datetime.now(tz=UTC)
    db.flush()
    return draft_row
