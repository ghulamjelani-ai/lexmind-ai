from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_tenant_db
from app.core.ratelimit import rate_limit
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import OrgOut, OrgRegisterRequest
from app.services.org_service import ProvisioningError, provision_organization

router = APIRouter(prefix="/orgs", tags=["organizations"])


@router.post(
    "/register",
    response_model=OrgOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit("register", 5, 3600))],
)
def register_org(body: OrgRegisterRequest, db: Session = Depends(get_db)) -> Organization:
    """Bootstrap a new chamber with its owner account and seeded system roles.

    This is the sign-up entry point for a new tenant. Staff are added afterward
    via invites / user management (not open self-registration into an existing org).
    """
    try:
        org, _owner = provision_organization(
            db,
            org_name=body.org_name,
            org_slug=body.org_slug,
            owner_email=body.owner_email,
            owner_password=body.owner_password,
            owner_name=body.owner_name,
        )
    except ProvisioningError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    db.commit()
    return org


@router.get("/me", response_model=OrgOut)
def my_org(
    db: Session = Depends(get_tenant_db), user: User = Depends(get_current_user)
) -> Organization:
    org = db.get(Organization, user.organization_id)
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return org
