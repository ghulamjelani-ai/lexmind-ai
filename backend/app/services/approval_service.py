"""Approval workflow for high-impact items (documents, reports, record changes)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.rbac import AuthContext
from app.models.approval import Approval
from app.schemas.approval import ApprovalCreate


def _now() -> datetime:
    return datetime.now(tz=UTC)


def create_approval(db: Session, ctx: AuthContext, data: ApprovalCreate) -> Approval:
    approval = Approval(
        organization_id=ctx.organization_id,
        target_type=data.target_type,
        target_id=data.target_id,
        status="pending",
        requested_by=ctx.user_id,
        approver_id=data.approver_id,
        comment=data.comment,
    )
    db.add(approval)
    db.flush()
    return approval


def get_approval(db: Session, ctx: AuthContext, approval_id: uuid.UUID) -> Approval | None:
    return db.scalar(
        select(Approval).where(
            Approval.id == approval_id, Approval.organization_id == ctx.organization_id
        )
    )


def list_approvals(
    db: Session, ctx: AuthContext, *, status: str | None = None, limit: int = 50, offset: int = 0
) -> tuple[list[Approval], int]:
    conditions = [Approval.organization_id == ctx.organization_id]
    if status:
        conditions.append(Approval.status == status)
    total = db.scalar(select(func.count()).select_from(Approval).where(*conditions)) or 0
    rows = list(
        db.scalars(
            select(Approval)
            .where(*conditions)
            .order_by(Approval.created_at.desc())
            .limit(limit)
            .offset(offset)
        ).all()
    )
    return rows, total


def decide(
    db: Session, ctx: AuthContext, approval: Approval, approve: bool, comment: str | None
) -> Approval:
    approval.status = "approved" if approve else "rejected"
    approval.approver_id = ctx.user_id
    approval.decided_at = _now()
    if comment:
        approval.comment = comment
    db.flush()
    return approval
