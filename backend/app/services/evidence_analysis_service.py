"""Evidence analysis: an on-demand, read-only view over a case's documents.
Unlike the case analysis report it is not persisted — it is a lens a lawyer runs
when they want the supporting/contradicting/missing map, always re-derived from the
current indexed documents so it never goes stale."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.ai import evidence_analysis
from app.ai.evidence_analysis import EvidenceResult
from app.core.rbac import AuthContext
from app.models.case import Case


def analyze(db: Session, ctx: AuthContext, case: Case) -> EvidenceResult:
    return evidence_analysis.analyze(db, ctx, case)
