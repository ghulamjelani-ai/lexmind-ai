"""Shared FastAPI dependencies: current user, auth context, permission gates."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rbac import AuthContext
from app.db.session import get_db
from app.models.user import User
from app.services import audit_service, auth_service
from app.services.rbac_service import build_auth_context


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    settings = get_settings()
    raw = request.cookies.get(settings.session_cookie_name, "")
    user = auth_service.resolve_session(db, raw)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return user


def get_auth_context(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> AuthContext:
    return build_auth_context(db, user)


def require(permission_code: str) -> Callable[..., AuthContext]:
    """Dependency factory gating an endpoint on a permission code."""

    def dependency(
        request: Request,
        db: Session = Depends(get_db),
        ctx: AuthContext = Depends(get_auth_context),
    ) -> AuthContext:
        if not ctx.has(permission_code):
            audit_service.record(
                db,
                action=f"authz.deny:{permission_code}",
                result="deny",
                organization_id=ctx.organization_id,
                actor_id=ctx.user_id,
                ip=_client_ip(request),
                user_agent=request.headers.get("user-agent"),
            )
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
            )
        return ctx

    return dependency
