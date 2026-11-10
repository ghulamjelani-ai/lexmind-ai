from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_tenant_db, require
from app.core.rbac import AuthContext
from app.schemas.reports import CaseSummaryOut
from app.services import reports_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary", response_model=CaseSummaryOut)
def case_summary(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("analytics:view")),
) -> CaseSummaryOut:
    """Case portfolio statistics, scoped to the cases the caller may read."""
    return CaseSummaryOut(**reports_service.case_summary(db, ctx))


@router.get("/cases.csv")
def cases_csv(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("analytics:view")),
) -> StreamingResponse:
    """CSV export of the caller's accessible cases."""
    return StreamingResponse(
        reports_service.cases_csv(db, ctx),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="cases.csv"'},
    )
