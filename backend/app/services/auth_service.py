"""Authentication: credential checks and server-side session lifecycle."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    generate_session_token,
    hash_password,
    hash_token,
    needs_rehash,
    verify_password,
)
from app.models.auth import UserSession
from app.models.organization import Organization
from app.models.user import User


def _now() -> datetime:
    return datetime.now(tz=UTC)


def authenticate(db: Session, org_slug: str, email: str, password: str) -> User | None:
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
    if not verify_password(password, user.password_hash):
        return None
    # Transparently upgrade the hash if Argon2 parameters have changed.
    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(password)
    user.last_login_at = _now()
    db.flush()
    return user


def change_password(db: Session, user: User, current_password: str, new_password: str) -> bool:
    """Verify the current password and set a new one. Returns False if the
    current password is wrong (no change made).

    ``user`` comes from the auth session and is detached, so re-load it on the
    given (tenant) session — otherwise the update is never persisted.
    """
    u = db.get(User, user.id)
    if u is None:
        return False
    if not verify_password(current_password, u.password_hash):
        return False
    u.password_hash = hash_password(new_password)
    db.flush()
    return True


def update_profile(db: Session, user: User, full_name: str) -> User:
    """Update the signed-in user's own profile fields. ``user`` is detached, so
    re-load it on the given session before writing."""
    u = db.get(User, user.id)
    if u is None:
        raise ValueError("User not found")
    u.full_name = full_name.strip()
    db.flush()
    return u


def create_session(
    db: Session, user: User, ip: str | None = None, user_agent: str | None = None
) -> str:
    """Create a session row and return the RAW token for the client cookie."""
    settings = get_settings()
    raw = generate_session_token()
    session = UserSession(
        organization_id=user.organization_id,
        user_id=user.id,
        token_hash=hash_token(raw),
        expires_at=_now() + timedelta(hours=settings.session_ttl_hours),
        ip=ip,
        user_agent=(user_agent or "")[:512] or None,
    )
    db.add(session)
    db.flush()
    return raw


def resolve_session(db: Session, raw_token: str) -> User | None:
    if not raw_token:
        return None
    session = db.scalar(
        select(UserSession).where(UserSession.token_hash == hash_token(raw_token))
    )
    if session is None or session.revoked_at is not None:
        return None
    expires = session.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    if expires < _now():
        return None
    user = db.get(User, session.user_id)
    if user is None or user.deleted_at is not None or user.status != "active":
        return None
    return user


def revoke_session(db: Session, raw_token: str) -> None:
    session = db.scalar(
        select(UserSession).where(UserSession.token_hash == hash_token(raw_token))
    )
    if session is not None and session.revoked_at is None:
        session.revoked_at = _now()
        db.flush()
