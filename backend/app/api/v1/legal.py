from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.ai import citation_check, legal_research
from app.api.deps import get_tenant_db, require
from app.core.rbac import AuthContext
from app.schemas.common import Page
from app.schemas.legal import (
    AutoVerifyOut,
    JudgmentCreate,
    JudgmentOut,
    LegalReferenceOut,
    LegalResearchRequest,
    LegalResearchResponse,
    ProvisionCreate,
    ProvisionOut,
    SourceOut,
    VerifyRequest,
)
from app.services import legal_service

router = APIRouter(prefix="/legal", tags=["legal"])


@router.get("/sources", response_model=list[SourceOut])
def list_sources(
    ctx: AuthContext = Depends(require("ai:research:run")),
) -> list[SourceOut]:
    """Official legal sources the platform prefers (and links to for manual
    verification when automated verification isn't available)."""
    return [SourceOut(**vars(s)) for s in legal_service.list_sources()]


@router.post("/research", response_model=LegalResearchResponse)
def research(
    body: LegalResearchRequest,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("ai:research:run")),
) -> LegalResearchResponse:
    """Answer a legal question grounded only in official-source search results,
    with verification-tagged citations (never fabricated)."""
    result = legal_research.research(db, ctx, body.question)
    db.commit()
    return LegalResearchResponse(
        answer=result.answer,
        references=[LegalReferenceOut(**vars(r)) for r in result.references],
        searched_domains=result.searched_domains,
        note=result.note,
    )


# --- legislation -------------------------------------------------------------
@router.post("/provisions", response_model=ProvisionOut, status_code=201)
def create_provision(
    body: ProvisionCreate,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("ai:research:run")),
) -> ProvisionOut:
    p = legal_service.create_provision(db, ctx, body)
    db.commit()
    db.refresh(p)
    return ProvisionOut.model_validate(p)


@router.get("/provisions", response_model=Page[ProvisionOut])
def list_provisions(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("ai:research:run")),
    status_: str | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> Page[ProvisionOut]:
    rows, total = legal_service.list_provisions(
        db, ctx, status=status_, q=q, limit=limit, offset=offset
    )
    return Page[ProvisionOut](
        items=[ProvisionOut.model_validate(p) for p in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("/provisions/{provision_id}/verify", response_model=ProvisionOut)
def verify_provision(
    provision_id: uuid.UUID,
    body: VerifyRequest,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("ai:research:run")),
) -> ProvisionOut:
    p = legal_service.get_provision(db, ctx, provision_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Provision not found")
    p = legal_service.verify_provision(db, p, status=body.status, source_url=body.source_url)
    db.commit()
    db.refresh(p)
    return ProvisionOut.model_validate(p)


@router.post("/provisions/{provision_id}/auto-verify", response_model=AutoVerifyOut)
def auto_verify_provision(
    provision_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("ai:research:run")),
) -> AutoVerifyOut:
    """Cross-check the cited section against official-source content and set the
    verification status automatically. Only confirms what the sources support —
    it never marks a citation verified on absence of evidence."""
    p = legal_service.get_provision(db, ctx, provision_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Provision not found")
    verdict = citation_check.verify_provision(db, ctx, p)
    db.commit()
    db.refresh(p)
    return AutoVerifyOut(
        provision=ProvisionOut.model_validate(p),
        status=verdict.status,
        matched_url=verdict.matched_url,
        note=verdict.note,
    )


# --- judgments ---------------------------------------------------------------
@router.post("/judgments", response_model=JudgmentOut, status_code=201)
def create_judgment(
    body: JudgmentCreate,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("ai:research:run")),
) -> JudgmentOut:
    j = legal_service.create_judgment(db, ctx, body)
    db.commit()
    db.refresh(j)
    return JudgmentOut.model_validate(j)


@router.get("/judgments", response_model=Page[JudgmentOut])
def list_judgments(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("ai:research:run")),
    status_: str | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> Page[JudgmentOut]:
    rows, total = legal_service.list_judgments(
        db, ctx, status=status_, q=q, limit=limit, offset=offset
    )
    return Page[JudgmentOut](
        items=[JudgmentOut.model_validate(j) for j in rows], total=total, limit=limit, offset=offset
    )


@router.post("/judgments/{judgment_id}/verify", response_model=JudgmentOut)
def verify_judgment(
    judgment_id: uuid.UUID,
    body: VerifyRequest,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("ai:research:run")),
) -> JudgmentOut:
    j = legal_service.get_judgment(db, ctx, judgment_id)
    if j is None:
        raise HTTPException(status_code=404, detail="Judgment not found")
    j = legal_service.verify_judgment(
        db, j, status=body.status, source_url=body.source_url, treatment=body.treatment
    )
    db.commit()
    db.refresh(j)
    return JudgmentOut.model_validate(j)
