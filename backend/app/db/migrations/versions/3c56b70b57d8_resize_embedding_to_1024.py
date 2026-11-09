"""resize embedding to 1024

Resize kb_chunks.embedding from vector(64) (mock) to vector(1024) to match a
real embedding model (voyage-law-2). Existing embeddings are cleared — re-index
knowledge-base documents (POST /documents/{id}/index) or re-ingest afterwards.
No-op on SQLite (JSON column has no fixed dimension).

Revision ID: 3c56b70b57d8
Revises: 44a941388d5f
Create Date: 2026-11-09
"""
from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "3c56b70b57d8"
down_revision: str | None = "44a941388d5f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    op.execute("DROP INDEX IF EXISTS ix_kb_chunks_embedding")
    op.execute("ALTER TABLE kb_chunks DROP COLUMN IF EXISTS embedding")
    op.execute("ALTER TABLE kb_chunks ADD COLUMN embedding vector(1024)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_kb_chunks_embedding "
        "ON kb_chunks USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    op.execute("DROP INDEX IF EXISTS ix_kb_chunks_embedding")
    op.execute("ALTER TABLE kb_chunks DROP COLUMN IF EXISTS embedding")
    op.execute("ALTER TABLE kb_chunks ADD COLUMN embedding vector(64)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_kb_chunks_embedding "
        "ON kb_chunks USING hnsw (embedding vector_cosine_ops)"
    )
