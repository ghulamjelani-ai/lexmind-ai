"""add email verifications

Pre-tenant OTP table for email-verified signup (no organization_id, no RLS;
accessed only via the privileged connection). Additive — safe on deploy.

Revision ID: c8f2a1d4e6b0
Revises: b7e4c9a12f30
Create Date: 2026-11-13
"""
from __future__ import annotations

from collections.abc import Sequence

import app.db.base
import sqlalchemy as sa
from alembic import op

revision: str = "c8f2a1d4e6b0"
down_revision: str | None = "b7e4c9a12f30"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "email_verifications",
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("purpose", sa.String(length=40), nullable=False),
        sa.Column("code_hash", sa.String(length=128), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", app.db.base.GUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("email_verifications", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_email_verifications_email"), ["email"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("email_verifications", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_email_verifications_email"))
    op.drop_table("email_verifications")
