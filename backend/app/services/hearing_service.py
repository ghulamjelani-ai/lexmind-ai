"""Hearings and the chamber calendar."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core import constants as C
from app.core.rbac import SCOPE_ALL, SCOPE_ASSIGNED, SCOPE_OWN, AuthContext
from app.models.case import Case, CaseAssignment, CaseEvent
from app.models.hearing import Hearing
from app.models.task import Task
from app.schemas.hearing import CalendarItem, HearingCreate, HearingUpdate


def create_hearing(db: Session, ctx: AuthContext, case: Case, data: HearingCreate) -> Hearing:
    hearing = Hearing(
        organization_id=ctx.organization_id,
        case_id=case.id,
        court_name=data.court_name,
        scheduled_at=data.scheduled_at,
        status=C.DEFAULT_HEARING_STATUS,  # unconfirmed until matched to an official source
        notes=data.notes,
        created_by=ctx.user_id,
    )
    db.add(hearing)
    db.flush()
    db.add(
        CaseEvent(
            organization_id=ctx.organization_id,
            case_id=case.id,
            event_type=C.EVENT_HEARING_SCHEDULED,
            actor_id=ctx.user_id,
            payload_json={"scheduled_at": data.scheduled_at.isoformat(), "status": hearing.status},
        )
    )
    # Reflect the earliest upcoming hearing on the case for convenience.
    case.next_hearing_date = data.scheduled_at.date()
    db.flush()
    return hearing


def list_hearings(db: Session, case: Case) -> list[Hearing]:
    return list(
        db.scalars(
            select(Hearing).where(Hearing.case_id == case.id).order_by(Hearing.scheduled_at)
        ).all()
    )


def get_hearing(db: Session, ctx: AuthContext, hearing_id: uuid.UUID) -> Hearing | None:
    return db.scalar(
        select(Hearing).where(
            Hearing.id == hearing_id, Hearing.organization_id == ctx.organization_id
        )
    )


def update_hearing(db: Session, hearing: Hearing, data: HearingUpdate) -> Hearing:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(hearing, field, value)
    db.flush()
    return hearing


def confirm_hearing(db: Session, hearing: Hearing, source: str) -> Hearing:
    hearing.status = "confirmed"
    hearing.confirmation_source = source
    db.flush()
    return hearing


def _accessible_case_ids(ctx: AuthContext):
    """Subquery/condition fragment for cases the caller may read."""
    scope = ctx.scope_for("cases:read")
    if scope == SCOPE_ALL:
        return None  # all org cases
    if scope == SCOPE_ASSIGNED:
        assigned = select(CaseAssignment.case_id).where(CaseAssignment.user_id == ctx.user_id)
        return or_(Case.assigned_lawyer_id == ctx.user_id, Case.id.in_(assigned))
    if scope == SCOPE_OWN:
        return Case.created_by == ctx.user_id
    return False  # no access


def calendar(
    db: Session, ctx: AuthContext, start: datetime, end: datetime
) -> list[CalendarItem]:
    """Hearings (and due tasks) within [start, end] for cases the caller can see."""
    case_cond = _accessible_case_ids(ctx)
    if case_cond is False:
        return []

    visible_cases = select(Case.id).where(
        Case.organization_id == ctx.organization_id, Case.deleted_at.is_(None)
    )
    if case_cond is not None:
        visible_cases = visible_cases.where(case_cond)

    items: list[CalendarItem] = []

    hearings = db.scalars(
        select(Hearing).where(
            Hearing.organization_id == ctx.organization_id,
            Hearing.case_id.in_(visible_cases),
            Hearing.scheduled_at >= start,
            Hearing.scheduled_at <= end,
        )
    ).all()
    for h in hearings:
        items.append(
            CalendarItem(
                kind="hearing", id=h.id, case_id=h.case_id,
                title=h.court_name or "Hearing", at=h.scheduled_at, status=h.status,
            )
        )

    tasks = db.scalars(
        select(Task).where(
            Task.organization_id == ctx.organization_id,
            Task.due_at.is_not(None),
            Task.due_at >= start,
            Task.due_at <= end,
            or_(Task.assignee_id == ctx.user_id, Task.created_by == ctx.user_id),
        )
    ).all()
    for t in tasks:
        items.append(
            CalendarItem(
                kind="task", id=t.id, case_id=t.case_id, title=t.title,
                at=t.due_at, status=t.status,
            )
        )

    items.sort(key=lambda i: i.at)
    return items
