"""Organization provisioning: create a chamber with its system roles and owner."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.rbac import OWNER
from app.core.security import hash_password
from app.models.organization import Organization
from app.models.user import User
from app.services import subscription_service
from app.services.rbac_service import assign_role, ensure_system_roles


class ProvisioningError(Exception):
    pass


def provision_organization(
    db: Session,
    *,
    org_name: str,
    org_slug: str,
    owner_email: str,
    owner_name: str,
    owner_password: str | None = None,
    owner_password_hash: str | None = None,
) -> tuple[Organization, User]:
    """Create an organization, seed system roles, and create its owner user.

    Pass either ``owner_password`` (hashed here) or a pre-computed
    ``owner_password_hash`` (used after OTP-verified signup)."""
    if not owner_password_hash:
        if not owner_password:
            raise ProvisioningError("A password or password hash is required")
        owner_password_hash = hash_password(owner_password)
    if db.scalar(select(Organization).where(Organization.slug == org_slug)):
        raise ProvisioningError(f"Organization slug '{org_slug}' already exists")

    org = Organization(name=org_name, slug=org_slug)
    db.add(org)
    db.flush()

    # Start a free trial from creation (Chamber-tier features for TRIAL_DAYS).
    subscription_service.start_trial_if_absent(db, org)

    roles = ensure_system_roles(db, org.id)

    owner = User(
        organization_id=org.id,
        email=owner_email.lower(),
        password_hash=owner_password_hash,
        full_name=owner_name,
        status="active",
    )
    db.add(owner)
    db.flush()
    assign_role(db, owner, roles[OWNER])
    return org, owner
