"""Test harness. Uses an in-memory SQLite database so the suite needs no
database server. The app's portable GUID type makes the same models run here
and on PostgreSQL in production.
"""

from __future__ import annotations

import os
import tempfile

# Must be set before any app module imports its settings/engine. Pin BOTH DB
# URLs so the suite never inherits a local .env (which may point at Postgres for
# host dev); both equal -> a single in-memory engine (auth == tenant).
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["APP_DATABASE_URL"] = "sqlite://"
os.environ["SECURE_COOKIES"] = "false"
# Force mock AI providers so the suite is hermetic — never calls (or bills) a real
# LLM/embedding API, even when a local .env configures openai/voyage with keys.
os.environ["AI_PROVIDER"] = "mock"
os.environ["EMBEDDING_PROVIDER"] = "mock"
# Isolate document storage to a temp dir for tests.
os.environ.setdefault("STORAGE_LOCAL_DIR", tempfile.mkdtemp(prefix="lexmind-test-storage-"))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.security import hash_password  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.org_service import provision_organization  # noqa: E402
from app.services.rbac_service import assign_role, ensure_system_roles  # noqa: E402


@pytest.fixture(autouse=True)
def _schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    return TestClient(app)


def make_org(db, slug: str, owner_email: str = "owner@x.pk", password: str = "OwnerPass123!"):
    org, owner = provision_organization(
        db,
        org_name=f"Org {slug}",
        org_slug=slug,
        owner_email=owner_email,
        owner_password=password,
        owner_name="Owner",
    )
    db.commit()
    return org, owner


def add_user(db, org_id, email, role_name, password="UserPass123!", is_client=False):
    roles = ensure_system_roles(db, org_id)
    user = User(
        organization_id=org_id,
        email=email.lower(),
        password_hash=hash_password(password),
        full_name="Test User",
        is_client=is_client,
        status="active",
    )
    db.add(user)
    db.flush()
    assign_role(db, user, roles[role_name])
    db.commit()
    return user


def login(client, org_slug, email, password):
    return client.post(
        "/api/v1/auth/login",
        json={"org_slug": org_slug, "email": email, "password": password},
    )
