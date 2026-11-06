from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_auth_context, get_tenant_db, require
from app.core.rbac import AuthContext
from app.schemas.approval import ApprovalCreate, ApprovalDecision, ApprovalOut
from app.schemas.common import Page
from app.services import approval_service, notification_service

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.post("", response_model=ApprovalOut, status_code=status.HTTP_201_CREATED)
def request_approval(
    body: ApprovalCreate,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> ApprovalOut:
    approval = approval_service.create_approval(db, ctx, body)
    if body.approver_id:
        notification_service.notify(
            db,
            organization_id=ctx.organization_id,
            user_id=body.approver_id,
            type="approval.requested",
            title="Approval requested",
            body=f"A {body.target_type} needs your approval.",
            payload={"approval_id": str(approval.id), "target_type": body.target_type},
        )
    db.commit()
    db.refresh(approval)
    return ApprovalOut.model_validate(approval)


@router.get("", response_model=Page[ApprovalOut])
def list_approvals(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("approvals:grant")),
    status_: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> Page[ApprovalOut]:
    rows, total = approval_service.list_approvals(
        db, ctx, status=status_, limit=limit, offset=offset
    )
    return Page[ApprovalOut](
        items=[ApprovalOut.model_validate(a) for a in rows], total=total, limit=limit, offset=offset
    )


@router.post("/{approval_id}/decide", response_model=ApprovalOut)
def decide_approval(
    approval_id: uuid.UUID,
    body: ApprovalDecision,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("approvals:grant")),
) -> ApprovalOut:
    approval = approval_service.get_approval(db, ctx, approval_id)
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    if approval.status != "pending":
        raise HTTPException(status_code=400, detail="Approval already decided")
    approval = approval_service.decide(db, ctx, approval, body.approve, body.comment)
    if approval.requested_by:
        notification_service.notify(
            db,
            organization_id=ctx.organization_id,
            user_id=approval.requested_by,
            type="approval.decided",
            title=f"Approval {approval.status}",
            body=f"Your {approval.target_type} was {approval.status}.",
            payload={"approval_id": str(approval.id), "status": approval.status},
        )
    db.commit()
    db.refresh(approval)
    return ApprovalOut.model_validate(approval)
