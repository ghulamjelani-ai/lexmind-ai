"""Case management: scope-aware access, timeline, assignments, parties.

This is where RBAC scopes finally bite: a user with ``cases:read`` at scope
``assigned`` only sees cases they are assigned to; ``own`` only cases they
created; ``all`` sees every case in the org (RLS already guarantees same-org).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import ColumnElement, and_, func, or_, select
from sqlalchemy.orm import Session

from app.core import constants as C
from app.core.rbac import SCOPE_ALL, SCOPE_ASSIGNED, SCOPE_OWN, AuthContext
from app.models.case import Case, CaseAssignment, CaseEvent, CaseParty
from app.models.user import User
from app.schemas.case import AssignmentIn, CaseCreate, CaseUpdate, PartyIn

SORT_FIELDS = {
    "created_at": Case.created_at,
    "updated_at": Case.updated_at,
    "next_hearing_date": Case.next_hearing_date,
    "title": Case.title,
}
_PRIORITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _event(db: Session, case: Case, event_type: str, actor_id, payload: dict) -> None:
    db.add(
        CaseEvent(
            organization_id=case.organization_id,
            case_id=case.id,
            event_type=event_type,
            actor_id=actor_id,
            payload_json=payload,
        )
    )


def _scope(ctx: AuthContext, action: str) -> str | None:
    return ctx.scope_for(action)


def _read_conditions(ctx: AuthContext) -> list[ColumnElement] | None:
    """Extra WHERE conditions for the caller's read scope, or None to deny."""
    scope = _scope(ctx, "cases:read")
    if scope is None:
        return None
    if scope == SCOPE_ALL:
        return []
    if scope == SCOPE_ASSIGNED:
        assigned = select(CaseAssignment.case_id).where(CaseAssignment.user_id == ctx.user_id)
        return [or_(Case.assigned_lawyer_id == ctx.user_id, Case.id.in_(assigned))]
    if scope == SCOPE_OWN:
        return [Case.created_by == ctx.user_id]
    return []


def can_access(db: Session, ctx: AuthContext, case: Case, action: str = "cases:read") -> bool:
    scope = _scope(ctx, action)
    if scope is None:
        return False
    if scope == SCOPE_ALL:
        return True
    if scope == SCOPE_OWN:
        return case.created_by == ctx.user_id
    if scope == SCOPE_ASSIGNED:
        if case.assigned_lawyer_id == ctx.user_id:
            return True
        return db.scalar(
            select(CaseAssignment.id).where(
                CaseAssignment.case_id == case.id, CaseAssignment.user_id == ctx.user_id
            )
        ) is not None
    return False


def create_case(db: Session, ctx: AuthContext, data: CaseCreate) -> Case:
    case = Case(
        organization_id=ctx.organization_id,
        title=data.title,
        category=data.category,
        custom_category=data.custom_category,
        client_id=data.client_id,
        opposite_party=data.opposite_party,
        case_number=data.case_number,
        court_name=data.court_name,
        judge_name=data.judge_name,
        police_station=data.police_station,
        fir_number=data.fir_number,
        district=data.district,
        province=data.province,
        status=data.status,
        priority=data.priority,
        filing_date=data.filing_date,
        next_hearing_date=data.next_hearing_date,
        description=data.description,
        legal_issues_json=data.legal_issues,
        assigned_lawyer_id=ctx.user_id,  # creator is primary by default
        created_by=ctx.user_id,
    )
    db.add(case)
    db.flush()

    db.add(
        CaseAssignment(
            organization_id=ctx.organization_id,
            case_id=case.id,
            user_id=ctx.user_id,
            role_on_case="primary",
            assigned_by=ctx.user_id,
        )
    )
    _event(db, case, C.EVENT_CASE_CREATED, ctx.user_id, {"title": case.title})
    _event(
        db, case, C.EVENT_LAWYER_ASSIGNED, ctx.user_id,
        {"user_id": str(ctx.user_id), "role": "primary"},
    )
    db.flush()
    return case


def get_case(db: Session, ctx: AuthContext, case_id: uuid.UUID) -> Case | None:
    case = db.scalar(
        select(Case).where(
            Case.id == case_id,
            Case.organization_id == ctx.organization_id,
            Case.deleted_at.is_(None),
        )
    )
    if case is None or not can_access(db, ctx, case, "cases:read"):
        return None
    return case


def list_cases(
    db: Session,
    ctx: AuthContext,
    *,
    q: str | None = None,
    status: str | None = None,
    category: str | None = None,
    priority: str | None = None,
    assigned_lawyer_id: uuid.UUID | None = None,
    client_id: uuid.UUID | None = None,
    sort: str = "created_at",
    order: str = "desc",
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Case], int]:
    scope_conditions = _read_conditions(ctx)
    if scope_conditions is None:
        return [], 0

    conditions = [
        Case.organization_id == ctx.organization_id,
        Case.deleted_at.is_(None),
        *scope_conditions,
    ]
    if q:
        like = f"%{q}%"
        conditions.append(
            or_(
                Case.title.ilike(like),
                Case.case_number.ilike(like),
                Case.fir_number.ilike(like),
                Case.opposite_party.ilike(like),
            )
        )
    if status:
        conditions.append(Case.status == status)
    if category:
        conditions.append(Case.category == category)
    if priority:
        conditions.append(Case.priority == priority)
    if assigned_lawyer_id:
        conditions.append(Case.assigned_lawyer_id == assigned_lawyer_id)
    if client_id:
        conditions.append(Case.client_id == client_id)

    where = and_(*conditions)
    total = db.scalar(select(func.count()).select_from(Case).where(where)) or 0

    if sort == "priority":
        from sqlalchemy import case as sa_case

        # Order by semantic priority rank (critical < high < medium < low).
        order_col = sa_case(_PRIORITY_RANK, value=Case.priority, else_=99)
    else:
        order_col = SORT_FIELDS.get(sort, Case.created_at)

    order_col = order_col.desc() if order == "desc" else order_col.asc()

    rows = list(
        db.scalars(select(Case).where(where).order_by(order_col).limit(limit).offset(offset)).all()
    )
    return rows, total


def update_case(db: Session, ctx: AuthContext, case: Case, data: CaseUpdate) -> Case:
    patch = data.model_dump(exclude_unset=True)
    if "legal_issues" in patch:
        case.legal_issues_json = patch.pop("legal_issues") or []

    old_status, old_priority = case.status, case.priority
    for field, value in patch.items():
        setattr(case, field, value)
    db.flush()

    if "status" in patch and patch["status"] != old_status:
        _event(db, case, C.EVENT_STATUS_CHANGED, ctx.user_id,
                {"from": old_status, "to": patch["status"]})
    if "priority" in patch and patch["priority"] != old_priority:
        _event(db, case, C.EVENT_PRIORITY_CHANGED, ctx.user_id,
                {"from": old_priority, "to": patch["priority"]})
    _event(db, case, C.EVENT_CASE_UPDATED, ctx.user_id, {"fields": sorted(patch.keys())})
    db.flush()
    return case


def assign_user(db: Session, ctx: AuthContext, case: Case, data: AssignmentIn) -> CaseAssignment:
    target = db.scalar(
        select(User).where(
            User.id == data.user_id,
            User.organization_id == ctx.organization_id,
            User.deleted_at.is_(None),
        )
    )
    if target is None:
        raise ValueError("User not found in this organization")

    assignment = db.scalar(
        select(CaseAssignment).where(
            CaseAssignment.case_id == case.id, CaseAssignment.user_id == data.user_id
        )
    )
    if assignment is None:
        assignment = CaseAssignment(
            organization_id=case.organization_id,
            case_id=case.id,
            user_id=data.user_id,
            role_on_case=data.role_on_case,
            assigned_by=ctx.user_id,
        )
        db.add(assignment)
    else:
        assignment.role_on_case = data.role_on_case

    if data.role_on_case == "primary":
        case.assigned_lawyer_id = data.user_id

    db.flush()
    _event(db, case, C.EVENT_LAWYER_ASSIGNED, ctx.user_id,
           {"user_id": str(data.user_id), "role": data.role_on_case})
    db.flush()
    return assignment


def list_assignments(db: Session, case: Case) -> list[CaseAssignment]:
    return list(
        db.scalars(select(CaseAssignment).where(CaseAssignment.case_id == case.id)).all()
    )


def add_party(db: Session, ctx: AuthContext, case: Case, data: PartyIn) -> CaseParty:
    party = CaseParty(
        organization_id=case.organization_id,
        case_id=case.id,
        name=data.name,
        party_type=data.party_type,
        details_json=data.details,
    )
    db.add(party)
    db.flush()
    _event(db, case, C.EVENT_PARTY_ADDED, ctx.user_id, {"name": data.name, "type": data.party_type})
    db.flush()
    return party


def list_parties(db: Session, case: Case) -> list[CaseParty]:
    return list(db.scalars(select(CaseParty).where(CaseParty.case_id == case.id)).all())


def add_note(db: Session, ctx: AuthContext, case: Case, note: str) -> CaseEvent:
    event = CaseEvent(
        organization_id=case.organization_id,
        case_id=case.id,
        event_type=C.EVENT_NOTE_ADDED,
        actor_id=ctx.user_id,
        payload_json={"note": note},
    )
    db.add(event)
    db.flush()
    return event


def timeline(db: Session, case: Case, *, limit: int = 100) -> list[CaseEvent]:
    return list(
        db.scalars(
            select(CaseEvent)
            .where(CaseEvent.case_id == case.id)
            .order_by(CaseEvent.occurred_at.desc())
            .limit(limit)
        ).all()
    )
