from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_tenant_db, require
from app.core.rbac import AuthContext
from app.schemas.case import CaseOut
from app.schemas.intake import ConvertIn, LeadCreate, LeadOut
from app.services import intake_service

router = APIRouter(prefix="/intake", tags=["intake"])


def _load(db: Session, ctx: AuthContext, lead_id: uuid.UUID):
    lead = intake_service.get(db, ctx, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/leads", response_model=LeadOut, status_code=201)
def create_lead(
    body: LeadCreate,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:create")),
) -> LeadOut:
    """Capture a prospective client and screen it for conflicts of interest at once."""
    lead = intake_service.create_lead(db, ctx, body.model_dump())
    db.commit()
    db.refresh(lead)
    return LeadOut.model_validate(lead)


@router.get("/leads", response_model=list[LeadOut])
def list_leads(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:read")),
    status_: str | None = Query(default=None, alias="status"),
) -> list[LeadOut]:
    return [LeadOut.model_validate(x) for x in intake_service.list_leads(db, ctx, status=status_)]


@router.post("/leads/{lead_id}/rescreen", response_model=LeadOut)
def rescreen_lead(
    lead_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:read")),
) -> LeadOut:
    lead = intake_service.rescreen(db, ctx, _load(db, ctx, lead_id))
    db.commit()
    db.refresh(lead)
    return LeadOut.model_validate(lead)


@router.post("/leads/{lead_id}/reject", response_model=LeadOut)
def reject_lead(
    lead_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:create")),
) -> LeadOut:
    lead = intake_service.reject(db, ctx, _load(db, ctx, lead_id))
    db.commit()
    db.refresh(lead)
    return LeadOut.model_validate(lead)


@router.post("/leads/{lead_id}/convert", response_model=CaseOut, status_code=201)
def convert_lead(
    lead_id: uuid.UUID,
    body: ConvertIn,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:create")),
) -> CaseOut:
    """Convert an approved lead into a client + case. A blocking conflict is refused
    unless the lawyer explicitly overrides."""
    lead = _load(db, ctx, lead_id)
    try:
        case = intake_service.convert(db, ctx, lead, category=body.category, override=body.override)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    db.commit()
    db.refresh(case)
    return CaseOut.model_validate(case)
