"""Hearing reminder dispatch.

Finds hearings coming up inside a window and sends an in-app reminder to the
people responsible for the case (the assigned lawyer and the case creator).
Idempotent: a given user is reminded about a given hearing at most once, so the
dispatcher can be run repeatedly (e.g. on a schedule) without spamming.
Operates within the caller's organization — RLS/org scoping still applies.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.rbac import AuthContext
from app.models.case import Case
from app.models.hearing import Hearing
from app.models.notification import Notification
from app.services import notification_service

REMINDER_TYPE = "hearing_reminder"
_INACTIVE_HEARING = {"held", "adjourned", "cancelled"}


def _already_reminded(db: Session, organization_id) -> set[tuple[str, str]]:
    """(hearing_id, user_id) pairs already reminded, to avoid duplicates."""
    rows = db.scalars(
        select(Notification).where(
            Notification.organization_id == organization_id,
            Notification.type == REMINDER_TYPE,
        )
    ).all()
    pairs: set[tuple[str, str]] = set()
    for n in rows:
        hid = n.payload_json.get("hearing_id") if n.payload_json else None
        if hid:
            pairs.add((str(hid), str(n.user_id)))
    return pairs


def dispatch(
    db: Session,
    ctx: AuthContext,
    *,
    within_hours: int = 48,
    now: datetime | None = None,
) -> int:
    """Create reminders for upcoming hearings; return how many were created."""
    now = now or datetime.now(tz=UTC)
    horizon = now + timedelta(hours=within_hours)

    hearings = db.scalars(
        select(Hearing).where(
            Hearing.organization_id == ctx.organization_id,
            Hearing.status.notin_(list(_INACTIVE_HEARING)),
            Hearing.scheduled_at >= now,
            Hearing.scheduled_at <= horizon,
        )
    ).all()
    if not hearings:
        return 0

    sent = _already_reminded(db, ctx.organization_id)
    created = 0
    for h in hearings:
        case = db.get(Case, h.case_id)
        if case is None or case.deleted_at is not None:
            continue
        recipients = {uid for uid in (case.assigned_lawyer_id, case.created_by) if uid is not None}
        when = h.scheduled_at.strftime("%Y-%m-%d %H:%M UTC")
        for uid in recipients:
            if (str(h.id), str(uid)) in sent:
                continue
            notification_service.notify(
                db,
                organization_id=ctx.organization_id,
                user_id=uid,
                type=REMINDER_TYPE,
                title=f"Upcoming hearing: {case.title}",
                body=f"Hearing scheduled for {when}"
                + (f" at {h.court_name}." if h.court_name else "."),
                payload={"hearing_id": str(h.id), "case_id": str(case.id)},
            )
            sent.add((str(h.id), str(uid)))
            created += 1
    return created
