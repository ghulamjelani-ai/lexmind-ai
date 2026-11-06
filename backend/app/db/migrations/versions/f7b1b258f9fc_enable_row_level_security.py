"""enable row level security

Defense-in-depth tenant isolation on PostgreSQL. Creates a restricted runtime
role (lexmind_app) and Row-Level Security policies that filter every tenant
table by the per-connection `app.current_org` GUC. The application sets that GUC
from the authenticated user's organization on each request.

This migration is a no-op on non-PostgreSQL backends (e.g. SQLite tests), where
app-layer scoping is the only guard.

Revision ID: f7b1b258f9fc
Revises: 44692056844a
Create Date: 2026-11-07
"""
from __future__ import annotations

import os
from collections.abc import Sequence

from alembic import op

revision: str = "f7b1b258f9fc"
down_revision: str | None = "44692056844a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

APP_ROLE = "lexmind_app"

# Tables whose own primary-key column IS the tenant id.
ORG_SELF = ["organizations"]

# Tenant tables scoped directly by an organization_id column.
ORG_SCOPED = [
    "users",
    "roles",
    "user_sessions",
    "invites",
    "password_reset_tokens",
    "audit_logs",
]

# Join tables with no organization_id — scoped via their parent role's org.
ROLE_SCOPED = ["user_roles", "role_permissions"]

# NULLIF maps an unset/empty GUC to NULL, so policies return no rows (rather
# than erroring on an empty-string -> uuid cast) when no tenant is set.
GUC = "NULLIF(current_setting('app.current_org', true), '')::uuid"


def _is_pg() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def upgrade() -> None:
    if not _is_pg():
        return

    app_password = os.environ.get("APP_DB_PASSWORD", "lexmind_app")
    db_name = op.get_bind().engine.url.database

    # 1. Restricted runtime role (idempotent).
    op.execute(
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{APP_ROLE}') THEN
                CREATE ROLE {APP_ROLE} LOGIN PASSWORD '{app_password}'
                    NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
            END IF;
        END
        $$;
        """
    )

    # 2. Grants: connect + schema usage + DML on existing and future tables.
    op.execute(f'GRANT CONNECT ON DATABASE "{db_name}" TO {APP_ROLE};')
    op.execute(f"GRANT USAGE ON SCHEMA public TO {APP_ROLE};")
    op.execute(
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {APP_ROLE};"
    )
    op.execute(f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {APP_ROLE};")
    op.execute(
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {APP_ROLE};"
    )

    # 3. RLS policies.
    # Organization sees only itself.
    for table in ORG_SELF:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        op.execute(
            f"CREATE POLICY tenant_isolation ON {table} FOR ALL "
            f"USING (id = {GUC}) WITH CHECK (id = {GUC});"
        )

    # Rows scoped by organization_id.
    for table in ORG_SCOPED:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        op.execute(
            f"CREATE POLICY tenant_isolation ON {table} FOR ALL "
            f"USING (organization_id = {GUC}) WITH CHECK (organization_id = {GUC});"
        )

    # Join tables scoped via their parent role's organization.
    for table in ROLE_SCOPED:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        op.execute(
            f"CREATE POLICY tenant_isolation ON {table} FOR ALL "
            f"USING (EXISTS (SELECT 1 FROM roles r WHERE r.id = {table}.role_id "
            f"AND r.organization_id = {GUC})) "
            f"WITH CHECK (EXISTS (SELECT 1 FROM roles r WHERE r.id = {table}.role_id "
            f"AND r.organization_id = {GUC}));"
        )

    # permissions is a global catalog: read-only for the app role, no RLS.
    op.execute(f"GRANT SELECT ON permissions TO {APP_ROLE};")


def downgrade() -> None:
    if not _is_pg():
        return

    for table in ORG_SELF + ORG_SCOPED + ROLE_SCOPED:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table};")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")

    db_name = op.get_bind().engine.url.database
    op.execute(
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
        f"REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLES FROM {APP_ROLE};"
    )
    op.execute(f"REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM {APP_ROLE};")
    op.execute(f"REVOKE ALL ON ALL TABLES IN SCHEMA public FROM {APP_ROLE};")
    op.execute(f"REVOKE USAGE ON SCHEMA public FROM {APP_ROLE};")
    op.execute(f'REVOKE CONNECT ON DATABASE "{db_name}" FROM {APP_ROLE};')
    op.execute(f"DROP ROLE IF EXISTS {APP_ROLE};")
