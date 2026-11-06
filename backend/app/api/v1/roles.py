from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require
from app.core.rbac import AuthContext
from app.db.session import get_db
from app.models.rbac import Role
from app.schemas.auth import RoleOut

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=list[RoleOut])
def list_roles(
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(require("admin:users:manage")),
) -> list[Role]:
    return list(
        db.scalars(select(Role).where(Role.organization_id == ctx.organization_id)).all()
    )
