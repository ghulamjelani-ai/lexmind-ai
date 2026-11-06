from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_auth_context, get_current_user
from app.core.config import get_settings
from app.core.rbac import AuthContext
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, MeOut, MessageOut, UserOut
from app.services import audit_service, auth_service
from app.services.rbac_service import build_auth_context

router = APIRouter(prefix="/auth", tags=["auth"])


def _ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _set_session_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=settings.session_ttl_hours * 3600,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        path="/",
    )


@router.post("/login", response_model=MeOut)
def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> MeOut:
    user = auth_service.authenticate(db, body.org_slug, body.email, body.password)
    if user is None:
        audit_service.record(
            db,
            action="auth.login",
            result="deny",
            ip=_ip(request),
            user_agent=request.headers.get("user-agent"),
            metadata={"org_slug": body.org_slug, "email": body.email},
        )
        db.commit()
        # Do not reveal whether org/email exists.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token = auth_service.create_session(
        db, user, ip=_ip(request), user_agent=request.headers.get("user-agent")
    )
    audit_service.record(
        db,
        action="auth.login",
        result="allow",
        organization_id=user.organization_id,
        actor_id=user.id,
        ip=_ip(request),
    )
    db.commit()
    _set_session_cookie(response, token)

    ctx = build_auth_context(db, user)
    return MeOut(
        user=UserOut.model_validate(user),
        permissions={code: sorted(scopes) for code, scopes in ctx.permissions.items()},
    )


@router.post("/logout", response_model=MessageOut)
def logout(request: Request, response: Response, db: Session = Depends(get_db)) -> MessageOut:
    settings = get_settings()
    raw = request.cookies.get(settings.session_cookie_name, "")
    if raw:
        auth_service.revoke_session(db, raw)
        db.commit()
    response.delete_cookie(settings.session_cookie_name, path="/")
    return MessageOut(message="Logged out")


@router.get("/me", response_model=MeOut)
def me(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    ctx: AuthContext = Depends(get_auth_context),
) -> MeOut:
    return MeOut(
        user=UserOut.model_validate(user),
        permissions={code: sorted(scopes) for code, scopes in ctx.permissions.items()},
    )
