"""Client intake: capture a lead, screen it for conflicts, and convert it into a
client + case only after a lawyer approves — never automatically."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.rbac import AuthContext
from app.models.case import Case, CaseEvent, CaseParty
from app.models.client import Client
from app.models.lead import Lead
from app.services import conflict_service


def _screen(db: Session, ctx: AuthContext, lead: Lead) -> None:
    report = conflict_service.screen(
        db,
        ctx,
        full_name=lead.full_name,
        opposing_party=lead.opposing_party,
        email=lead.email,
        phone=lead.phone,
    )
    lead.conflict_level = report.level
    lead.conflict_hits_json = report.as_dicts()
    lead.screened_at = datetime.now(tz=UTC)


def create_lead(db: Session, ctx: AuthContext, data: dict) -> Lead:
    lead = Lead(
        organization_id=ctx.organization_id,
        full_name=data["full_name"],
        email=data.get("email"),
        phone=data.get("phone"),
        opposing_party=data.get("opposing_party"),
        matter_type=data.get("matter_type"),
        description=data.get("description"),
        status="new",
        created_by=ctx.user_id,
    )
    db.add(lead)
    _screen(db, ctx, lead)
    db.flush()
    return lead


def rescreen(db: Session, ctx: AuthContext, lead: Lead) -> Lead:
    _screen(db, ctx, lead)
    db.flush()
    return lead


def list_leads(db: Session, ctx: AuthContext, *, status: str | None = None) -> list[Lead]:
    conditions = [Lead.organization_id == ctx.organization_id]
    if status:
        conditions.append(Lead.status == status)
    return list(
        db.scalars(select(Lead).where(*conditions).order_by(Lead.created_at.desc())).all()
    )


def get(db: Session, ctx: AuthContext, lead_id: uuid.UUID) -> Lead | None:
    return db.scalar(
        select(Lead).where(
            Lead.id == lead_id, Lead.organization_id == ctx.organization_id
        )
    )


def reject(db: Session, ctx: AuthContext, lead: Lead) -> Lead:
    lead.status = "rejected"
    db.flush()
    return lead


def convert(db: Session, ctx: AuthContext, lead: Lead, *, category: str, override: bool) -> Case:
    """Turn an approved lead into a client + case. A blocking conflict stops the
    conversion unless the lawyer explicitly overrides (recorded on the timeline)."""
    if lead.status == "converted":
        raise ValueError("Lead already converted.")
    if lead.conflict_level == "block" and not override:
        raise ValueError(
            "This lead has a blocking conflict of interest. Resolve it or convert with "
            "an explicit override."
        )

    client = Client(
        organization_id=ctx.organization_id,
        full_name=lead.full_name,
        email=lead.email,
        phone=lead.phone,
        created_by=ctx.user_id,
    )
    db.add(client)
    db.flush()

    case = Case(
        organization_id=ctx.organization_id,
        title=f"{lead.matter_type or 'Matter'} — {lead.full_name}",
        category=category,
        client_id=client.id,
        opposite_party=lead.opposing_party,
        description=lead.description,
        created_by=ctx.user_id,
    )
    db.add(case)
    db.flush()

    if lead.opposing_party:
        db.add(
            CaseParty(
                organization_id=ctx.organization_id,
                case_id=case.id,
                name=lead.opposing_party,
                party_type="opposite",
            )
        )
    db.add(
        CaseEvent(
            organization_id=ctx.organization_id,
            case_id=case.id,
            event_type="converted_from_lead",
            actor_id=ctx.user_id,
            payload_json={
                "lead_id": str(lead.id),
                "conflict_level": lead.conflict_level,
                "override": bool(override and lead.conflict_level == "block"),
            },
        )
    )

    lead.status = "converted"
    lead.converted_case_id = case.id
    db.flush()
    return case
