from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai import tax_assistant
from app.api.deps import get_tenant_db, require
from app.core import tax_pk
from app.core.rbac import AuthContext
from app.schemas.tax import TaxAnswerOut, TaxQueryIn, TaxReferenceOut

router = APIRouter(prefix="/tax", tags=["tax"])


@router.get("/reference", response_model=TaxReferenceOut)
def tax_reference(
    ctx: AuthContext = Depends(require("ai:research:run")),
) -> TaxReferenceOut:
    """Curated, source-linked Pakistan tax reference (filer/non-filer, deadlines,
    NTN and chamber registration). Static authoritative content — no AI involved."""
    return TaxReferenceOut(**tax_pk.reference())


@router.post("/ask", response_model=TaxAnswerOut)
def tax_ask(
    body: TaxQueryIn,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("ai:research:run")),
) -> TaxAnswerOut:
    """Ask the tax assistant. The query is validated first: an empty, too-short or
    off-topic query is rejected locally (forwarded_to_ai = false) and never reaches
    the model, so a malformed command costs no tokens."""
    result = tax_assistant.answer(db, ctx, body.query)
    db.commit()
    return TaxAnswerOut(
        forwarded_to_ai=result.forwarded_to_ai,
        answer=result.answer,
        sources=result.sources,
        disclaimer=result.disclaimer,
        model_used=result.model_used,
        rejection_code=result.rejection_code,
        examples=result.examples,
    )
