"""Client portal — strictly scoped to the signed-in client's own records."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_tenant_db
from app.models.user import User
from app.services import portal_service

router = APIRouter(prefix="/portal", tags=["portal"])


@router.get("/me")
def portal_overview(
    db: Session = Depends(get_tenant_db),
    user: User = Depends(get_current_user),
) -> dict:
    """The current client's own cases and invoices. Empty when the account is
    not linked to any client record."""
    data = portal_service.overview(db, user)
    db.commit()  # persist a first-time auto-link
    return data
