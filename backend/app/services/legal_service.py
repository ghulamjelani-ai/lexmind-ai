"""Legal reference cache: legislation and judgments, with explicit verification.

Nothing is auto-marked "verified": references start "pending", and a qualified
user (or, later, an automated check against an official source) sets the status.
This is the non-fabrication spine from docs/architecture/09.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.legal_sources import (
    DEFAULT_VERIFICATION_STATUS,
    OFFICIAL_SOURCES,
    LegalSource,
)
from app.core.rbac import AuthContext
from app.models.legal import Judgment, LegalProvision
from app.schemas.legal import JudgmentCreate, ProvisionCreate


def list_sources() -> list[LegalSource]:
    return OFFICIAL_SOURCES


def _now() -> datetime:
    return datetime.now(tz=UTC)


# --- provisions --------------------------------------------------------------
def create_provision(db: Session, ctx: AuthContext, data: ProvisionCreate) -> LegalProvision:
    provision = LegalProvision(
        organization_id=ctx.organization_id,
        law_name=data.law_name,
        section=data.section,
        text=data.text,
        source_key=data.source_key,
        source_url=data.source_url,
        verification_status=DEFAULT_VERIFICATION_STATUS,  # never auto-verified
        created_by=ctx.user_id,
    )
    db.add(provision)
    db.flush()
    return provision


def get_provision(db: Session, ctx: AuthContext, provision_id: uuid.UUID) -> LegalProvision | None:
    return db.scalar(
        select(LegalProvision).where(
            LegalProvision.id == provision_id,
            LegalProvision.organization_id == ctx.organization_id,
        )
    )


def list_provisions(
    db: Session, ctx: AuthContext, *, status: str | None, q: str | None, limit: int, offset: int
) -> tuple[list[LegalProvision], int]:
    conditions = [LegalProvision.organization_id == ctx.organization_id]
    if status:
        conditions.append(LegalProvision.verification_status == status)
    if q:
        conditions.append(LegalProvision.law_name.ilike(f"%{q}%"))
    total = db.scalar(select(func.count()).select_from(LegalProvision).where(*conditions)) or 0
    rows = list(
        db.scalars(
            select(LegalProvision)
            .where(*conditions)
            .order_by(LegalProvision.created_at.desc())
            .limit(limit)
            .offset(offset)
        ).all()
    )
    return rows, total


def verify_provision(
    db: Session, provision: LegalProvision, *, status: str, source_url: str | None
) -> LegalProvision:
    provision.verification_status = status
    if source_url:
        provision.source_url = source_url
    provision.retrieved_at = _now()
    db.flush()
    return provision


# --- judgments ---------------------------------------------------------------
def create_judgment(db: Session, ctx: AuthContext, data: JudgmentCreate) -> Judgment:
    judgment = Judgment(
        organization_id=ctx.organization_id,
        title=data.title,
        citation=data.citation,
        court=data.court,
        judgment_date=data.judgment_date,
        source_url=data.source_url,
        verification_status=DEFAULT_VERIFICATION_STATUS,
        created_by=ctx.user_id,
    )
    db.add(judgment)
    db.flush()
    return judgment


def get_judgment(db: Session, ctx: AuthContext, judgment_id: uuid.UUID) -> Judgment | None:
    return db.scalar(
        select(Judgment).where(
            Judgment.id == judgment_id, Judgment.organization_id == ctx.organization_id
        )
    )


def list_judgments(
    db: Session, ctx: AuthContext, *, status: str | None, q: str | None, limit: int, offset: int
) -> tuple[list[Judgment], int]:
    conditions = [Judgment.organization_id == ctx.organization_id]
    if status:
        conditions.append(Judgment.verification_status == status)
    if q:
        conditions.append(Judgment.title.ilike(f"%{q}%"))
    total = db.scalar(select(func.count()).select_from(Judgment).where(*conditions)) or 0
    rows = list(
        db.scalars(
            select(Judgment)
            .where(*conditions)
            .order_by(Judgment.created_at.desc())
            .limit(limit)
            .offset(offset)
        ).all()
    )
    return rows, total


def verify_judgment(
    db: Session, judgment: Judgment, *, status: str, source_url: str | None, treatment: str | None
) -> Judgment:
    judgment.verification_status = status
    if source_url:
        judgment.source_url = source_url
    if treatment:
        judgment.treatment = treatment
    judgment.retrieved_at = _now()
    db.flush()
    return judgment
