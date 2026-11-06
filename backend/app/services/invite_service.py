"""Invitation flow: an admin invites a user to a role; the invitee accepts with
a token and sets their own password (no open self-registration into an org).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import generate_session_token, hash_password, hash_token
from app.models.auth import Invite
from app.models.rbac import Role
from app.models.user import User
from app.services.rbac_service import assign_role


class InviteError(Exception):
    pass


def _now() -> datetime:
    return datetime.now(tz=UTC)


def create_invite(
    db: Session,
    *,
    organization_id: uuid.UUID,
    email: str,
    role_name: str,
    invited_by: uuid.UUID,
) -> tuple[Invite, str]:
    role = db.scalar(
        select(Role).where(Role.organization_id == organization_id, Role.name == role_name)
    )
    if role is None:
        raise InviteError(f"Unknown role '{role_name}'")

    existing_user = db.scalar(
        select(User).where(
            User.organization_id == organization_id, User.email == email.lower()
        )
    )
    if existing_user is not None:
        raise InviteError("A user with this email already exists")

    raw = generate_session_token()
    invite = Invite(
        organization_id=organization_id,
        email=email.lower(),
        role_id=role.id,
        token_hash=hash_token(raw),
        expires_at=_now() + timedelta(hours=get_settings().invite_ttl_hours),
        invited_by=invited_by,
    )
    db.add(invite)
    db.flush()
    return invite, raw


def accept_invite(db: Session, raw_token: str, full_name: str, password: str) -> User:
    invite = db.scalar(select(Invite).where(Invite.token_hash == hash_token(raw_token)))
    if invite is None or invite.accepted_at is not None:
        raise InviteError("Invalid or already-used invitation")
    expires = invite.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    if expires < _now():
        raise InviteError("Invitation has expired")

    # Guard against a race where the email was registered after the invite.
    if db.scalar(
        select(User).where(
            User.organization_id == invite.organization_id, User.email == invite.email
        )
    ):
        raise InviteError("A user with this email already exists")

    role = db.get(Role, invite.role_id) if invite.role_id else None
    is_client = role is not None and role.name == "client"

    user = User(
        organization_id=invite.organization_id,
        email=invite.email,
        password_hash=hash_password(password),
        full_name=full_name,
        is_client=is_client,
        status="active",
    )
    db.add(user)
    db.flush()
    if role is not None:
        assign_role(db, user, role)
    invite.accepted_at = _now()
    db.flush()
    return user
