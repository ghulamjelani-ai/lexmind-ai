from __future__ import annotations

import uuid
from datetime import UTC

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_tenant_db, require
from app.core.rbac import AuthContext
from app.models.case import Case
from app.schemas.case import (
    AssignmentIn,
    AssignmentOut,
    CaseCreate,
    CaseOut,
    CaseUpdate,
    EventOut,
    NoteIn,
    PartyIn,
    PartyOut,
)
from app.schemas.common import Page
from app.services import case_service

router = APIRouter(prefix="/cases", tags=["cases"])


def _load_case(db: Session, ctx: AuthContext, case_id: uuid.UUID, action: str) -> Case:
    """Load an org case and enforce the caller's instance-level scope for `action`.
    Returns 404 (not 403) when not accessible, so case existence is not leaked."""
    case = db.scalar(
        select(Case).where(
            Case.id == case_id,
            Case.organization_id == ctx.organization_id,
            Case.deleted_at.is_(None),
        )
    )
    if case is None or not case_service.can_access(db, ctx, case, action):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


@router.post("", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
def create_case(
    body: CaseCreate,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:create")),
) -> CaseOut:
    case = case_service.create_case(db, ctx, body)
    db.commit()
    db.refresh(case)
    return CaseOut.model_validate(case)


@router.get("", response_model=Page[CaseOut])
def list_cases(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:read")),
    q: str | None = Query(default=None),
    status_: str | None = Query(default=None, alias="status"),
    category: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    assigned_lawyer_id: uuid.UUID | None = Query(default=None),
    client_id: uuid.UUID | None = Query(default=None),
    sort: str = Query(default="created_at"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> Page[CaseOut]:
    rows, total = case_service.list_cases(
        db,
        ctx,
        q=q,
        status=status_,
        category=category,
        priority=priority,
        assigned_lawyer_id=assigned_lawyer_id,
        client_id=client_id,
        sort=sort,
        order=order,
        limit=limit,
        offset=offset,
    )
    return Page[CaseOut](
        items=[CaseOut.model_validate(c) for c in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{case_id}", response_model=CaseOut)
def get_case(
    case_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:read")),
) -> CaseOut:
    return CaseOut.model_validate(_load_case(db, ctx, case_id, "cases:read"))


@router.patch("/{case_id}", response_model=CaseOut)
def update_case(
    case_id: uuid.UUID,
    body: CaseUpdate,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:update")),
) -> CaseOut:
    case = _load_case(db, ctx, case_id, "cases:update")
    case = case_service.update_case(db, ctx, case, body)
    db.commit()
    db.refresh(case)
    return CaseOut.model_validate(case)


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case(
    case_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:delete")),
) -> None:
    from datetime import datetime

    case = _load_case(db, ctx, case_id, "cases:delete")
    case.deleted_at = datetime.now(tz=UTC)
    db.commit()


# --- assignments -------------------------------------------------------------
@router.post("/{case_id}/assignments", response_model=AssignmentOut, status_code=201)
def assign_case(
    case_id: uuid.UUID,
    body: AssignmentIn,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:assign")),
) -> AssignmentOut:
    case = _load_case(db, ctx, case_id, "cases:assign")
    try:
        assignment = case_service.assign_user(db, ctx, case, body)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    db.commit()
    db.refresh(assignment)
    return AssignmentOut.model_validate(assignment)


@router.get("/{case_id}/assignments", response_model=list[AssignmentOut])
def case_assignments(
    case_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:read")),
) -> list[AssignmentOut]:
    case = _load_case(db, ctx, case_id, "cases:read")
    return [AssignmentOut.model_validate(a) for a in case_service.list_assignments(db, case)]


# --- parties -----------------------------------------------------------------
@router.post("/{case_id}/parties", response_model=PartyOut, status_code=201)
def add_party(
    case_id: uuid.UUID,
    body: PartyIn,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:update")),
) -> PartyOut:
    case = _load_case(db, ctx, case_id, "cases:update")
    party = case_service.add_party(db, ctx, case, body)
    db.commit()
    db.refresh(party)
    return PartyOut.model_validate(party)


@router.get("/{case_id}/parties", response_model=list[PartyOut])
def case_parties(
    case_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:read")),
) -> list[PartyOut]:
    case = _load_case(db, ctx, case_id, "cases:read")
    return [PartyOut.model_validate(p) for p in case_service.list_parties(db, case)]


# --- notes & timeline --------------------------------------------------------
@router.post("/{case_id}/notes", response_model=EventOut, status_code=201)
def add_note(
    case_id: uuid.UUID,
    body: NoteIn,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:update")),
) -> EventOut:
    case = _load_case(db, ctx, case_id, "cases:update")
    event = case_service.add_note(db, ctx, case, body.note)
    db.commit()
    db.refresh(event)
    return EventOut.model_validate(event)


@router.get("/{case_id}/timeline", response_model=list[EventOut])
def case_timeline(
    case_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:read")),
) -> list[EventOut]:
    case = _load_case(db, ctx, case_id, "cases:read")
    return [EventOut.model_validate(e) for e in case_service.timeline(db, case)]
