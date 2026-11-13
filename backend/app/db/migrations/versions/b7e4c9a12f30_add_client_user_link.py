"""add client user link

Link a client *user* (an is_client account) to their client *record* so a
client portal can scope strictly to their own cases/documents. Additive and
nullable — safe on populated tables (no FK constraint, to keep the deploy-time
`alembic upgrade head` bulletproof; integrity is enforced in the service layer).

Revision ID: b7e4c9a12f30
Revises: 762be3ff7942
Create Date: 2026-11-13
"""
from __future__ import annotations

from collections.abc import Sequence

import app.db.base
import sqlalchemy as sa
from alembic import op

revision: str = "b7e4c9a12f30"
down_revision: str | None = "762be3ff7942"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("clients", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", app.db.base.GUID(), nullable=True))
        batch_op.create_index(batch_op.f("ix_clients_user_id"), ["user_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("clients", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_clients_user_id"))
        batch_op.drop_column("user_id")
