"""pgvector native embeddings

Replace the portable JSON embedding column on kb_chunks with a native pgvector
column (+ HNSW cosine index) on PostgreSQL. On other backends (SQLite tests) the
column is swapped to a JSON column so the chain stays consistent.

NOTE: existing kb_chunks rows lose their embeddings (the JSON column is dropped);
re-ingest knowledge-base documents after upgrading.

Revision ID: 44a941388d5f
Revises: ee6a6144677c
Create Date: 2026-11-08
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "44a941388d5f"
down_revision: str | None = "ee6a6144677c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

EMBED_DIM = 64


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
        op.execute("ALTER TABLE kb_chunks DROP COLUMN IF EXISTS embedding_json")
        op.execute(f"ALTER TABLE kb_chunks ADD COLUMN embedding vector({EMBED_DIM})")
        op.execute(
            "CREATE INDEX IF NOT EXISTS ix_kb_chunks_embedding "
            "ON kb_chunks USING hnsw (embedding vector_cosine_ops)"
        )
    else:
        with op.batch_alter_table("kb_chunks", schema=None) as batch_op:
            batch_op.drop_column("embedding_json")
            batch_op.add_column(sa.Column("embedding", sa.JSON(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP INDEX IF EXISTS ix_kb_chunks_embedding")
        op.execute("ALTER TABLE kb_chunks DROP COLUMN IF EXISTS embedding")
        op.execute("ALTER TABLE kb_chunks ADD COLUMN embedding_json JSON NOT NULL DEFAULT '[]'")
    else:
        with op.batch_alter_table("kb_chunks", schema=None) as batch_op:
            batch_op.drop_column("embedding")
            batch_op.add_column(sa.Column("embedding_json", sa.JSON(), nullable=False))
