from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_auth_context, get_current_user, get_tenant_db
from app.core.config import get_settings
from app.core.email import send_email
from app.core.ratelimit import rate_limit
from app.core.rbac import AuthContext
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    MeOut,
    MessageOut,
    MfaCodeIn,
    MfaEnrollOut,
    PasswordChangeIn,
    PasswordResetConfirmIn,
    PasswordResetRequestIn,
    UserOut,
)
from app.services import audit_service, auth_service, mfa_service, password_reset_service
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
        samesite=settings.cookie_samesite,  # "none" for cross-host API/web in prod
        path="/",
    )


@router.post(
    "/login",
    response_model=MeOut,
    dependencies=[Depends(rate_limit("login", 10, 60))],
)
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

    if not mfa_service.verify_login(user, body.mfa_code):
        audit_service.record(
            db,
            action="auth.login",
            result="deny",
            organization_id=user.organization_id,
            actor_id=user.id,
            ip=_ip(request),
            metadata={"reason": "mfa_required"},
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="MFA code required or invalid",
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
    response.delete_cookie(
        settings.session_cookie_name,
        path="/",
        samesite=settings.cookie_samesite,
        secure=settings.secure_cookies,
    )
    return MessageOut(message="Logged out")


@router.get("/me", response_model=MeOut)
def me(
    user: User = Depends(get_current_user),
    ctx: AuthContext = Depends(get_auth_context),
) -> MeOut:
    return MeOut(
        user=UserOut.model_validate(user),
        permissions={code: sorted(scopes) for code, scopes in ctx.permissions.items()},
    )


# --- MFA (TOTP) --------------------------------------------------------------
@router.post("/mfa/enroll", response_model=MfaEnrollOut)
def mfa_enroll(
    db: Session = Depends(get_tenant_db), user: User = Depends(get_current_user)
) -> MfaEnrollOut:
    db_user = db.get(User, user.id)
    secret, uri = mfa_service.enroll(db, db_user)
    db.commit()
    return MfaEnrollOut(secret=secret, otpauth_uri=uri)


@router.post("/mfa/activate", response_model=MessageOut)
def mfa_activate(
    body: MfaCodeIn,
    db: Session = Depends(get_tenant_db),
    user: User = Depends(get_current_user),
) -> MessageOut:
    try:
        mfa_service.activate(db, db.get(User, user.id), body.code)
    except mfa_service.MFAError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    db.commit()
    return MessageOut(message="MFA enabled")


@router.post("/mfa/disable", response_model=MessageOut)
def mfa_disable(
    body: MfaCodeIn,
    db: Session = Depends(get_tenant_db),
    user: User = Depends(get_current_user),
) -> MessageOut:
    try:
        mfa_service.disable(db, db.get(User, user.id), body.code)
    except mfa_service.MFAError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    db.commit()
    return MessageOut(message="MFA disabled")


# --- Password reset ----------------------------------------------------------
@router.post(
    "/password-reset/request",
    response_model=MessageOut,
    dependencies=[Depends(rate_limit("pwreset", 5, 300))],
)
def password_reset_request(
    body: PasswordResetRequestIn, db: Session = Depends(get_db)
) -> MessageOut:
    # Always returns the same message (no account enumeration).
    token = password_reset_service.request_reset(db, body.org_slug, body.email)
    db.commit()
    if token:
        settings = get_settings()
        reset_url = f"{settings.app_url.rstrip('/')}/reset-password?token={token}"
        send_email(
            body.email,
            "Reset your LexMind password",
            (
                "We received a request to reset your LexMind password.\n\n"
                f"Reset it here (valid for {settings.password_reset_ttl_minutes} minutes):\n"
                f"{reset_url}\n\n"
                "If you didn't request this, you can safely ignore this email."
            ),
        )
    return MessageOut(message="If the account exists, a reset link has been sent.")


@router.post(
    "/password-reset/confirm",
    response_model=MessageOut,
    dependencies=[Depends(rate_limit("pwreset_confirm", 10, 300))],
)
def password_reset_confirm(
    body: PasswordResetConfirmIn, db: Session = Depends(get_db)
) -> MessageOut:
    ok = password_reset_service.confirm_reset(db, body.token, body.new_password)
    db.commit()
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )
    return MessageOut(message="Password updated")


@router.post(
    "/password/change",
    response_model=MessageOut,
    dependencies=[Depends(rate_limit("pwchange", 10, 300))],
)
def password_change(
    body: PasswordChangeIn,
    db: Session = Depends(get_tenant_db),
    user: User = Depends(get_current_user),
) -> MessageOut:
    """Change the signed-in user's own password (requires the current one)."""
    ok = auth_service.change_password(db, user, body.current_password, body.new_password)
    if not ok:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect"
        )
    db.commit()
    return MessageOut(message="Password changed")
