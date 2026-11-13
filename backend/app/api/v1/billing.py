"""Billing & subscription status.

``GET /billing/subscription`` returns the recomputed subscription state and
entitlements for the current organization (used by the app to show warnings and
to enforce restrictions in the UI). ``POST /billing/subscription/activate`` marks
a plan paid for the next period — called by an admin after a confirmed payment
(e.g. a Pakistani bank transfer / JazzCash / EasyPaisa), and the same entry point
a payment-gateway webhook would use once one is configured.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_auth_context, get_tenant_db, require
from app.core.plans import PLANS
from app.core.rbac import AuthContext
from app.models.organization import Organization
from app.services import subscription_service

router = APIRouter(prefix="/billing", tags=["billing"])


class ActivatePlanIn(BaseModel):
    plan: str = Field(min_length=1, max_length=50)
    period_days: int = Field(default=30, ge=1, le=366)


def _org(db: Session, ctx: AuthContext) -> Organization:
    org = db.get(Organization, ctx.organization_id)
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return org


@router.get("/subscription")
def get_subscription(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> dict:
    return subscription_service.summary(_org(db, ctx))


@router.post("/subscription/activate")
def activate_plan(
    body: ActivatePlanIn,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("admin:users:manage")),
) -> dict:
    if body.plan not in PLANS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown plan '{body.plan}'")
    org = _org(db, ctx)
    subscription_service.mark_paid(db, org, body.plan, period_days=body.period_days)
    db.commit()
    return subscription_service.summary(org)
