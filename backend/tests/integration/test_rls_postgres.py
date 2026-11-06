"""PostgreSQL Row-Level Security integration test.

Skipped unless both are set (RLS is a Postgres-only backstop):
  LEXMIND_TEST_PG_URL      — privileged/owner URL (schema already migrated)
  LEXMIND_TEST_APP_PG_URL  — restricted lexmind_app URL

Run against the dev container, e.g.:
  LEXMIND_TEST_PG_URL=postgresql+psycopg://lexmind:lexmind@localhost:5433/lexmind \
  LEXMIND_TEST_APP_PG_URL=postgresql+psycopg://lexmind_app:lexmind_app@localhost:5433/lexmind \
  uv run pytest tests/integration -q
"""

from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import sessionmaker

from app.services.org_service import provision_organization

OWNER_URL = os.environ.get("LEXMIND_TEST_PG_URL")
APP_URL = os.environ.get("LEXMIND_TEST_APP_PG_URL")

pytestmark = pytest.mark.skipif(
    not (OWNER_URL and APP_URL),
    reason="Set LEXMIND_TEST_PG_URL and LEXMIND_TEST_APP_PG_URL to run RLS tests",
)


@pytest.fixture(scope="module")
def two_orgs():
    owner_engine = create_engine(OWNER_URL)
    Session = sessionmaker(bind=owner_engine)
    tag = uuid.uuid4().hex[:8]
    with Session() as db:
        a, _ = provision_organization(
            db, org_name="A", org_slug=f"rls-a-{tag}",
            owner_email=f"a-{tag}@a.pk", owner_password="Passw0rd123!", owner_name="A",
        )
        b, _ = provision_organization(
            db, org_name="B", org_slug=f"rls-b-{tag}",
            owner_email=f"b-{tag}@b.pk", owner_password="Passw0rd123!", owner_name="B",
        )
        db.commit()
        return str(a.id), str(b.id)


def _set_org(conn, org_id: str | None):
    conn.execute(text("SELECT set_config('app.current_org', :o, false)"), {"o": org_id or ""})


def test_unset_guc_sees_no_rows(two_orgs):
    app_engine = create_engine(APP_URL)
    with app_engine.connect() as c:
        _set_org(c, None)
        assert c.execute(text("SELECT count(*) FROM users")).scalar() == 0


def test_guc_scopes_to_single_org(two_orgs):
    org_a, org_b = two_orgs
    app_engine = create_engine(APP_URL)
    with app_engine.connect() as c:
        _set_org(c, org_a)
        seen = [str(r[0]) for r in c.execute(text("SELECT DISTINCT organization_id FROM users"))]
        assert seen == [org_a]
        assert c.execute(
            text("SELECT count(*) FROM users WHERE organization_id = :b"), {"b": org_b}
        ).scalar() == 0

        _set_org(c, org_b)
        seen = [str(r[0]) for r in c.execute(text("SELECT DISTINCT organization_id FROM users"))]
        assert seen == [org_b]


def test_organizations_table_scoped(two_orgs):
    org_a, _ = two_orgs
    app_engine = create_engine(APP_URL)
    with app_engine.connect() as c:
        _set_org(c, org_a)
        rows = [str(r[0]) for r in c.execute(text("SELECT id FROM organizations"))]
        assert rows == [org_a]


def test_with_check_blocks_cross_org_insert(two_orgs):
    org_a, org_b = two_orgs
    app_engine = create_engine(APP_URL)
    with app_engine.connect() as c:
        _set_org(c, org_a)
        with pytest.raises(DatabaseError):
            c.execute(
                text(
                    "INSERT INTO users (id, organization_id, email, password_hash, full_name,"
                    " status, is_client, mfa_enabled, created_at, updated_at) VALUES "
                    "(gen_random_uuid(), :b, 'evil@x.pk', 'x', 'Evil', 'active', false, false,"
                    " now(), now())"
                ),
                {"b": org_b},
            )
            c.commit()
