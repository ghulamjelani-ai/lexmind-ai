"""Database engine, session factory, and the FastAPI DB dependency.

Tenant isolation is enforced primarily in the service/query layer (every
tenant query filters by organization_id from the authenticated context).
On PostgreSQL, Row-Level Security policies (added via migration) act as a
defense-in-depth backstop.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def build_engine(database_url: str) -> Engine:
    """Create an engine, handling SQLite (tests) and PostgreSQL (prod)."""
    if database_url.startswith("sqlite"):
        from sqlalchemy.pool import StaticPool

        connect_args = {"check_same_thread": False}
        # In-memory SQLite needs a shared static pool so all sessions see the
        # same database within a test run.
        if ":memory:" in database_url or database_url.endswith("sqlite://"):
            return create_engine(
                database_url,
                connect_args=connect_args,
                poolclass=StaticPool,
            )
        return create_engine(database_url, connect_args=connect_args)
    return create_engine(database_url, pool_pre_ping=True)


engine: Engine = build_engine(get_settings().database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
