from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require
from app.core.rbac import AuthContext
from app.db.session import get_db
from app.models.auth import Invite
from app.models.user import User
from app.schemas.auth import (
    InviteAcceptIn,
    InviteCreatedOut,
    InviteCreateIn,
    InviteOut,
    UserOut,
)
from app.services import invite_service

router = APIRouter(prefix="/invites", tags=["invites"])


@router.post("", response_model=InviteCreatedOut, status_code=status.HTTP_201_CREATED)
def create_invite(
    body: InviteCreateIn,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(require("admin:users:manage")),
) -> InviteCreatedOut:
    try:
        invite, token = invite_service.create_invite(
            db,
            organization_id=ctx.organization_id,
            email=body.email,
            role_name=body.role,
            invited_by=ctx.user_id,
        )
    except invite_service.InviteError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    db.commit()
    return InviteCreatedOut(id=invite.id, email=invite.email, role=body.role, token=token)


@router.get("", response_model=list[InviteOut])
def list_invites(
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(require("admin:users:manage")),
) -> list[InviteOut]:
    rows = db.scalars(
        select(Invite).where(Invite.organization_id == ctx.organization_id)
    ).all()
    return [
        InviteOut(id=i.id, email=i.email, accepted=i.accepted_at is not None) for i in rows
    ]


@router.post("/accept", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def accept_invite(body: InviteAcceptIn, db: Session = Depends(get_db)) -> User:
    try:
        user = invite_service.accept_invite(db, body.token, body.full_name, body.password)
    except invite_service.InviteError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    db.commit()
    db.refresh(user)
    return user
