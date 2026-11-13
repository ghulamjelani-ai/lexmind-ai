"""Shared FastAPI dependencies: current user, tenant DB session, auth context,
permission gates.

Request flow for a tenant endpoint:
  1. get_current_user  -> resolves the session token on the PRIVILEGED connection
                          (pre-tenant bootstrap), returns a detached User.
  2. get_tenant_db     -> opens the RESTRICTED connection and sets app.current_org
                          to the user's org, so RLS scopes every query.
  3. get_auth_context  -> builds the effective-permission context on that session.
"""

from __future__ import annotations

from collections.abc import Callable, Generator

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rbac import AuthContext
from app.db.session import (
    AppSessionLocal,
    AuthSessionLocal,
    get_db,
    reset_current_org,
    set_current_org,
)
from app.models.organization import Organization
from app.models.user import User
from app.services import audit_service, auth_service, subscription_service
from app.services.rbac_service import build_auth_context

__all__ = [
    "get_db",
    "get_current_user",
    "get_tenant_db",
    "get_auth_context",
    "require",
]


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def get_current_user(request: Request) -> User:
    """Resolve the session cookie on a short-lived privileged session.

    The session is closed before the request's tenant session opens, so on
    SQLite (single shared connection) the two never overlap.
    """
    settings = get_settings()
    raw = request.cookies.get(settings.session_cookie_name, "")
    db = AuthSessionLocal()
    try:
        user = auth_service.resolve_session(db, raw)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )
        db.expunge(user)  # detach so attributes stay readable after close
        return user
    finally:
        db.close()


def get_tenant_db(user: User = Depends(get_current_user)) -> Generator[Session, None, None]:
    """RLS-scoped session for the authenticated user's organization."""
    db = AppSessionLocal()
    try:
        set_current_org(db, user.organization_id)
        yield db
    finally:
        reset_current_org(db)
        db.close()


def get_auth_context(
    db: Session = Depends(get_tenant_db), user: User = Depends(get_current_user)
) -> AuthContext:
    return build_auth_context(db, user)


def require(permission_code: str) -> Callable[..., AuthContext]:
    """Dependency factory gating an endpoint on a permission code."""

    def dependency(
        request: Request,
        db: Session = Depends(get_tenant_db),
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


def require_not_restricted(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> AuthContext:
    """Block paid write operations when the subscription is restricted (grace
    period elapsed). Reads and billing stay available so data is never lost and
    the customer can always pay to restore access."""
    org = db.get(Organization, ctx.organization_id)
    if org is not None and subscription_service.is_restricted(org):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Your subscription is past due. Please renew to continue. "
            "Your data remains available in read-only mode.",
        )
    return ctx
