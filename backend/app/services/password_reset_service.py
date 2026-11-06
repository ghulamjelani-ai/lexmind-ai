"""Secure password reset: request a single-use token, then confirm with it.

The request step never reveals whether an account exists. The raw token is
returned by the service to the caller (the API endpoint logs/emails it and does
NOT echo it in the response); tests consume the returned token directly.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import generate_session_token, hash_password, hash_token
from app.models.auth import UserSession
from app.models.organization import Organization
from app.models.password_reset import PasswordResetToken
from app.models.user import User


def _now() -> datetime:
    return datetime.now(tz=UTC)


def request_reset(db: Session, org_slug: str, email: str) -> str | None:
    """Create a reset token for the user if they exist. Returns the raw token
    (for the caller to deliver) or None if no matching active user."""
    org = db.scalar(select(Organization).where(Organization.slug == org_slug))
    if org is None:
        return None
    user = db.scalar(
        select(User).where(
            User.organization_id == org.id,
            User.email == email.lower(),
            User.deleted_at.is_(None),
        )
    )
    if user is None or user.status != "active":
        return None

    raw = generate_session_token()
    db.add(
        PasswordResetToken(
            organization_id=user.organization_id,
            user_id=user.id,
            token_hash=hash_token(raw),
            expires_at=_now() + timedelta(minutes=get_settings().password_reset_ttl_minutes),
        )
    )
    db.flush()
    return raw


def confirm_reset(db: Session, raw_token: str, new_password: str) -> bool:
    row = db.scalar(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == hash_token(raw_token)
        )
    )
    if row is None or row.used_at is not None:
        return False
    expires = row.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    if expires < _now():
        return False

    user = db.get(User, row.user_id)
    if user is None or user.deleted_at is not None:
        return False

    user.password_hash = hash_password(new_password)
    row.used_at = _now()

    # Invalidate all existing sessions for this user (force re-login).
    for session in db.scalars(
        select(UserSession).where(
            UserSession.user_id == user.id, UserSession.revoked_at.is_(None)
        )
    ).all():
        session.revoked_at = _now()

    db.flush()
    return True
