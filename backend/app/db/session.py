"""Database engines, session factories, and the FastAPI DB dependencies.

Two connections support defense-in-depth tenant isolation on PostgreSQL:

* **auth/privileged** (``database_url``): a superuser/owner used for migrations
  and the pre-tenant authentication bootstrap (resolve a session token, verify
  credentials). It bypasses RLS — necessary because these lookups happen before
  the tenant is known.
* **app/restricted** (``app_database_url``): a non-superuser role used for all
  tenant-scoped request handling. RLS policies filter every row by the
  ``app.current_org`` setting, which is set per request from the authenticated
  user's organization.

On SQLite (tests/dev) there are no roles or RLS; both fall back to a single
engine and the GUC calls are no-ops. App-layer scoping remains the primary
guard either way.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_settings = get_settings()


def build_engine(database_url: str) -> Engine:
    """Create an engine, handling SQLite (tests) and PostgreSQL (prod)."""
    if database_url.startswith("sqlite"):
        from sqlalchemy.pool import StaticPool

        connect_args = {"check_same_thread": False}
        if ":memory:" in database_url or database_url.endswith("sqlite://"):
            return create_engine(
                database_url, connect_args=connect_args, poolclass=StaticPool
            )
        return create_engine(database_url, connect_args=connect_args)
    return create_engine(database_url, pool_pre_ping=True)


_auth_url = _settings.database_url
_app_url = _settings.app_database_url or _settings.database_url

# Privileged engine (migrations + auth bootstrap).
auth_engine: Engine = build_engine(_auth_url)
# Restricted engine (tenant-scoped requests). Same object when URLs match so
# SQLite's single in-memory DB is shared across both.
app_engine: Engine = auth_engine if _app_url == _auth_url else build_engine(_app_url)

IS_POSTGRES: bool = auth_engine.dialect.name == "postgresql"

AuthSessionLocal = sessionmaker(bind=auth_engine, autoflush=False, expire_on_commit=False)
AppSessionLocal = sessionmaker(bind=app_engine, autoflush=False, expire_on_commit=False)

# Backward-compatible aliases (seed script, test harness, create_all target).
engine = auth_engine
SessionLocal = AuthSessionLocal


def set_current_org(session: Session, organization_id) -> None:
    """Set the tenant GUC for RLS on a PostgreSQL session (no-op elsewhere)."""
    if session.bind is not None and session.bind.dialect.name == "postgresql":
        session.execute(
            text("SELECT set_config('app.current_org', :org, false)"),
            {"org": str(organization_id)},
        )


def reset_current_org(session: Session) -> None:
    if session.bind is not None and session.bind.dialect.name == "postgresql":
        session.execute(text("SELECT set_config('app.current_org', '', false)"))


def get_db() -> Generator[Session, None, None]:
    """Privileged bootstrap session (public/auth endpoints). Not RLS-scoped."""
    db = AuthSessionLocal()
    try:
        yield db
    finally:
        db.close()
