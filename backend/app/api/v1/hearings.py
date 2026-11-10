from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_tenant_db, require
from app.core.rbac import AuthContext
from app.models.case import Case
from app.schemas.hearing import (
    CalendarItem,
    HearingConfirm,
    HearingCreate,
    HearingOut,
    HearingUpdate,
    ReminderDispatchOut,
)
from app.services import case_service, hearing_reminder_service, hearing_service

router = APIRouter(tags=["hearings"])


def _load_case(db: Session, ctx: AuthContext, case_id: uuid.UUID, action: str) -> Case:
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


@router.post("/cases/{case_id}/hearings", response_model=HearingOut, status_code=201)
def create_hearing(
    case_id: uuid.UUID,
    body: HearingCreate,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("hearings:manage")),
) -> HearingOut:
    case = _load_case(db, ctx, case_id, "cases:read")
    hearing = hearing_service.create_hearing(db, ctx, case, body)
    db.commit()
    db.refresh(hearing)
    return HearingOut.model_validate(hearing)


@router.get("/cases/{case_id}/hearings", response_model=list[HearingOut])
def list_hearings(
    case_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:read")),
) -> list[HearingOut]:
    case = _load_case(db, ctx, case_id, "cases:read")
    return [HearingOut.model_validate(h) for h in hearing_service.list_hearings(db, case)]


@router.patch("/hearings/{hearing_id}", response_model=HearingOut)
def update_hearing(
    hearing_id: uuid.UUID,
    body: HearingUpdate,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("hearings:manage")),
) -> HearingOut:
    hearing = hearing_service.get_hearing(db, ctx, hearing_id)
    if hearing is None:
        raise HTTPException(status_code=404, detail="Hearing not found")
    hearing = hearing_service.update_hearing(db, hearing, body)
    db.commit()
    db.refresh(hearing)
    return HearingOut.model_validate(hearing)


@router.post("/hearings/{hearing_id}/confirm", response_model=HearingOut)
def confirm_hearing(
    hearing_id: uuid.UUID,
    body: HearingConfirm,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("hearings:manage")),
) -> HearingOut:
    hearing = hearing_service.get_hearing(db, ctx, hearing_id)
    if hearing is None:
        raise HTTPException(status_code=404, detail="Hearing not found")
    hearing = hearing_service.confirm_hearing(db, hearing, body.confirmation_source)
    db.commit()
    db.refresh(hearing)
    return HearingOut.model_validate(hearing)


@router.post("/hearings/reminders/dispatch", response_model=ReminderDispatchOut)
def dispatch_reminders(
    within_hours: int = Query(default=48, ge=1, le=336),
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("hearings:manage")),
) -> ReminderDispatchOut:
    """Send in-app reminders for hearings due within the window. Idempotent —
    safe to call on a schedule; a user is reminded about a hearing only once."""
    created = hearing_reminder_service.dispatch(db, ctx, within_hours=within_hours)
    db.commit()
    return ReminderDispatchOut(reminders_created=created, within_hours=within_hours)


@router.get("/calendar", response_model=list[CalendarItem], tags=["calendar"])
def calendar(
    start: datetime = Query(..., alias="from"),
    end: datetime = Query(..., alias="to"),
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:read")),
) -> list[CalendarItem]:
    return hearing_service.calendar(db, ctx, start, end)
