"""Case analysis: generate the structured report, list, and approve (the human
gate — an analysis is a draft until a qualified lawyer approves it)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import case_analysis
from app.core.rbac import AuthContext
from app.models.case import Case, CaseEvent
from app.models.case_analysis import CaseAnalysis


def generate(db: Session, ctx: AuthContext, case: Case) -> CaseAnalysis:
    result = case_analysis.analyze(db, ctx, case)
    analysis = CaseAnalysis(
        organization_id=ctx.organization_id,
        case_id=case.id,
        report_json=result.report,
        status="draft",
        model_used=result.model_used,
        generated_by=ctx.user_id,
    )
    db.add(analysis)
    db.flush()
    db.add(
        CaseEvent(
            organization_id=ctx.organization_id,
            case_id=case.id,
            event_type="analysis_generated",
            actor_id=ctx.user_id,
            payload_json={"analysis_id": str(analysis.id), "chunks": result.chunks_used},
        )
    )
    db.flush()
    return analysis


def list_for_case(db: Session, case: Case) -> list[CaseAnalysis]:
    return list(
        db.scalars(
            select(CaseAnalysis)
            .where(CaseAnalysis.case_id == case.id)
            .order_by(CaseAnalysis.created_at.desc())
        ).all()
    )


def get(db: Session, ctx: AuthContext, analysis_id: uuid.UUID) -> CaseAnalysis | None:
    return db.scalar(
        select(CaseAnalysis).where(
            CaseAnalysis.id == analysis_id,
            CaseAnalysis.organization_id == ctx.organization_id,
        )
    )


def approve(db: Session, ctx: AuthContext, analysis: CaseAnalysis) -> CaseAnalysis:
    analysis.status = "approved"
    analysis.approved_by = ctx.user_id
    analysis.approved_at = datetime.now(tz=UTC)
    db.flush()
    return analysis
