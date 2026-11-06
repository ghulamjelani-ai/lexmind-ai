"""In-app notifications. Email dispatch is wired in a later phase; here we
persist notifications and expose read/unread. Other services call notify()."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.rbac import AuthContext
from app.models.notification import Notification


def notify(
    db: Session,
    *,
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
    type: str,
    title: str,
    body: str | None = None,
    payload: dict | None = None,
) -> Notification:
    n = Notification(
        organization_id=organization_id,
        user_id=user_id,
        channel="in_app",
        type=type,
        title=title,
        body=body,
        payload_json=payload or {},
    )
    db.add(n)
    db.flush()
    return n


def list_for_user(
    db: Session, ctx: AuthContext, *, unread_only: bool = False, limit: int = 50, offset: int = 0
) -> tuple[list[Notification], int]:
    conditions = [
        Notification.organization_id == ctx.organization_id,
        Notification.user_id == ctx.user_id,
    ]
    if unread_only:
        conditions.append(Notification.read_at.is_(None))
    total = db.scalar(select(func.count()).select_from(Notification).where(*conditions)) or 0
    rows = list(
        db.scalars(
            select(Notification)
            .where(*conditions)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
        ).all()
    )
    return rows, total


def unread_count(db: Session, ctx: AuthContext) -> int:
    return db.scalar(
        select(func.count())
        .select_from(Notification)
        .where(
            Notification.organization_id == ctx.organization_id,
            Notification.user_id == ctx.user_id,
            Notification.read_at.is_(None),
        )
    ) or 0


def mark_read(db: Session, ctx: AuthContext, notification_id: uuid.UUID) -> bool:
    n = db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.organization_id == ctx.organization_id,
            Notification.user_id == ctx.user_id,
        )
    )
    if n is None:
        return False
    if n.read_at is None:
        n.read_at = datetime.now(tz=UTC)
        db.flush()
    return True


def mark_all_read(db: Session, ctx: AuthContext) -> int:
    rows = db.scalars(
        select(Notification).where(
            Notification.organization_id == ctx.organization_id,
            Notification.user_id == ctx.user_id,
            Notification.read_at.is_(None),
        )
    ).all()
    now = datetime.now(tz=UTC)
    for n in rows:
        n.read_at = now
    db.flush()
    return len(rows)
