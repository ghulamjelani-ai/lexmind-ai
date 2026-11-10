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
from app.schemas.case_analysis import (
    CaseAnalysisOut,
    PriorityFactorOut,
    PriorityScoreOut,
)
from app.schemas.common import Page
from app.schemas.evidence_analysis import EvidenceAnalysisOut
from app.services import case_analysis_service, case_service, evidence_analysis_service

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


@router.get("/priority-queue", response_model=list[PriorityScoreOut])
def priority_queue(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:read")),
    limit: int = Query(default=25, ge=1, le=200),
) -> list[PriorityScoreOut]:
    """Accessible active cases ranked by an explainable urgency score — each
    result carries the factors (and points) that produced its rank."""
    from datetime import date

    from app.ai import prioritization

    cases = case_service.active_cases(db, ctx)
    ranked = prioritization.rank(cases, today=date.today())[:limit]
    return [
        PriorityScoreOut(
            case_id=s.case_id,
            title=s.title,
            score=s.score,
            level=s.level,
            factors=[PriorityFactorOut(**vars(f)) for f in s.factors],
        )
        for s in ranked
    ]


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


# --- AI case analysis --------------------------------------------------------
@router.post("/{case_id}/analysis", response_model=CaseAnalysisOut, status_code=201)
def generate_analysis(
    case_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("ai:analysis:request")),
) -> CaseAnalysisOut:
    case = _load_case(db, ctx, case_id, "cases:read")
    analysis = case_analysis_service.generate(db, ctx, case)
    db.commit()
    db.refresh(analysis)
    return CaseAnalysisOut.model_validate(analysis)


@router.get("/{case_id}/analysis", response_model=list[CaseAnalysisOut])
def list_analyses(
    case_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("cases:read")),
) -> list[CaseAnalysisOut]:
    case = _load_case(db, ctx, case_id, "cases:read")
    rows = case_analysis_service.list_for_case(db, case)
    return [CaseAnalysisOut.model_validate(a) for a in rows]


# --- AI evidence analysis (on-demand, not persisted) -------------------------
@router.post("/{case_id}/evidence-analysis", response_model=EvidenceAnalysisOut)
def analyze_evidence(
    case_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("ai:analysis:request")),
) -> EvidenceAnalysisOut:
    case = _load_case(db, ctx, case_id, "cases:read")
    result = evidence_analysis_service.analyze(db, ctx, case)
    db.commit()
    return EvidenceAnalysisOut(
        supporting=result.supporting,
        contradicting=result.contradicting,
        missing=result.missing,
        notes=result.notes,
        chunks_used=result.chunks_used,
    )


@router.post("/{case_id}/analysis/{analysis_id}/approve", response_model=CaseAnalysisOut)
def approve_analysis(
    case_id: uuid.UUID,
    analysis_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("approvals:grant")),
) -> CaseAnalysisOut:
    _load_case(db, ctx, case_id, "cases:read")
    analysis = case_analysis_service.get(db, ctx, analysis_id)
    if analysis is None or analysis.case_id != case_id:
        raise HTTPException(status_code=404, detail="Analysis not found")
    analysis = case_analysis_service.approve(db, ctx, analysis)
    db.commit()
    db.refresh(analysis)
    return CaseAnalysisOut.model_validate(analysis)
