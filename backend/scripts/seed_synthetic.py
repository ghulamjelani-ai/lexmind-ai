"""Seed a synthetic chamber with one user per role for local development.

SYNTHETIC DATA ONLY. Never run against a database holding real client data.

    uv run python -m scripts.seed_synthetic
"""

from __future__ import annotations

from sqlalchemy import select

from app.core.rbac import (
    CLERK,
    CLIENT,
    JUNIOR_ADVOCATE,
    LEGAL_RESEARCHER,
    SENIOR_ADVOCATE,
)
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.organization import Organization
from app.models.user import User
from app.services.org_service import provision_organization
from app.services.rbac_service import assign_role, ensure_system_roles

ORG_SLUG = "demo-chamber"
DEMO_PASSWORD = "DemoPass123!"  # noqa: S105 — synthetic local-dev credential

STAFF = [
    ("senior@demo.pk", "Sara Senior", SENIOR_ADVOCATE, False),
    ("junior@demo.pk", "Junaid Junior", JUNIOR_ADVOCATE, False),
    ("researcher@demo.pk", "Rida Researcher", LEGAL_RESEARCHER, False),
    ("clerk@demo.pk", "Kamran Clerk", CLERK, False),
    ("client@demo.pk", "Client One", CLIENT, True),
]


def main() -> None:
    # create_all is convenient for local seeding; production uses Alembic.
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.scalar(select(Organization).where(Organization.slug == ORG_SLUG))
        if existing:
            print(f"Organization '{ORG_SLUG}' already exists; nothing to seed.")
            return

        org, owner = provision_organization(
            db,
            org_name="Demo Chamber",
            org_slug=ORG_SLUG,
            owner_email="owner@demo.pk",
            owner_password=DEMO_PASSWORD,
            owner_name="Omar Owner",
        )
        roles = ensure_system_roles(db, org.id)

        for email, name, role_name, is_client in STAFF:
            user = User(
                organization_id=org.id,
                email=email,
                password_hash=hash_password(DEMO_PASSWORD),
                full_name=name,
                is_client=is_client,
                status="active",
            )
            db.add(user)
            db.flush()
            assign_role(db, user, roles[role_name])

        db.commit()

        print("Seeded synthetic chamber:")
        print(f"  org slug: {ORG_SLUG}")
        print("  owner:    owner@demo.pk  (role: owner)")
        for email, _name, role_name, _ in STAFF:
            print(f"  user:     {email}  (role: {role_name})")
        print(f"  password for all: {DEMO_PASSWORD}  [synthetic]")
    finally:
        db.close()


if __name__ == "__main__":
    main()
