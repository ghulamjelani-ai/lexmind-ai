from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require
from app.core.rbac import AuthContext
from app.core.security import hash_password
from app.db.session import get_db
from app.models.rbac import Role
from app.models.user import User
from app.schemas.auth import UserCreateRequest, UserOut
from app.services.rbac_service import assign_role

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(require("admin:users:manage")),
) -> list[User]:
    return list(
        db.scalars(
            select(User).where(
                User.organization_id == ctx.organization_id,
                User.deleted_at.is_(None),
            )
        ).all()
    )


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    body: UserCreateRequest,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(require("admin:users:manage")),
) -> User:
    role = db.scalar(
        select(Role).where(Role.organization_id == ctx.organization_id, Role.name == body.role)
    )
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown role '{body.role}'"
        )

    exists = db.scalar(
        select(User).where(
            User.organization_id == ctx.organization_id,
            User.email == body.email.lower(),
        )
    )
    if exists is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists"
        )

    user = User(
        organization_id=ctx.organization_id,
        email=body.email.lower(),
        password_hash=hash_password(body.password),
        full_name=body.full_name,
        is_client=body.is_client,
        status="active",
    )
    db.add(user)
    db.flush()
    assign_role(db, user, role)
    db.commit()
    db.refresh(user)
    return user
