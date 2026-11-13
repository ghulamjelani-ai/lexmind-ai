from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_tenant_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import OrgOut

router = APIRouter(prefix="/orgs", tags=["organizations"])

# Chamber creation is handled by the email-verified signup flow
# (POST /auth/register/start + /auth/register/verify), so there is no open
# /orgs/register endpoint — an account can only be created for an email whose
# owner proves control of it via the OTP.


@router.get("/me", response_model=OrgOut)
def my_org(
    db: Session = Depends(get_tenant_db), user: User = Depends(get_current_user)
) -> Organization:
    org = db.get(Organization, user.organization_id)
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return org
