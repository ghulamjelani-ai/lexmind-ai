"""RAG retrieval with per-request authorization filtering.

Embeddings are stored as JSON and scored with in-process cosine similarity, which
is portable across SQLite (tests) and Postgres. The production optimization is a
native pgvector column + ANN index; it replaces the scoring here without changing
the authorization rules, which are the security-critical part.
"""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.providers import get_provider
from app.core.rbac import AuthContext
from app.models.knowledge import KbChunk, KbDocument

CHUNK_SIZE = 800


def chunk_text(text: str, size: int = CHUNK_SIZE) -> list[str]:
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    buf = ""
    for p in paras or [text]:
        if len(buf) + len(p) + 2 <= size:
            buf = f"{buf}\n\n{p}" if buf else p
        else:
            if buf:
                chunks.append(buf)
            buf = p
    if buf:
        chunks.append(buf)
    return chunks or [text[:size]]


def ingest(
    db: Session,
    ctx: AuthContext,
    *,
    title: str,
    text: str,
    source_type: str,
    source_ref: str | None = None,
    case_id: uuid.UUID | None = None,
) -> KbDocument:
    doc = KbDocument(
        organization_id=ctx.organization_id,
        source_type=source_type,
        source_ref=source_ref,
        title=title,
        case_id=case_id,
        access_metadata_json={"case_id": str(case_id) if case_id else None},
        created_by=ctx.user_id,
    )
    db.add(doc)
    db.flush()

    pieces = chunk_text(text)
    embeddings = get_provider().embed(pieces)
    for i, (piece, emb) in enumerate(zip(pieces, embeddings, strict=True)):
        db.add(
            KbChunk(
                organization_id=ctx.organization_id,
                kb_document_id=doc.id,
                case_id=case_id,
                chunk_index=i,
                text=piece,
                embedding_json=emb,
            )
        )
    db.flush()
    return doc


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


@dataclass
class RetrievedChunk:
    chunk_id: uuid.UUID
    kb_document_id: uuid.UUID
    case_id: uuid.UUID | None
    text: str
    score: float
    source_ref: str | None


def retrieve(
    db: Session,
    ctx: AuthContext,
    query: str,
    *,
    case_id: uuid.UUID | None,
    top_k: int,
) -> list[RetrievedChunk]:
    """Return the top-k chunks the caller is authorized to see.

    Authorization (enforced here, before ranking):
      * case mode (case_id given): chunks for THAT case + org-wide chunks.
      * general mode (case_id None): ONLY org-wide chunks (case_id IS NULL) —
        case documents never leak into general chat.
    The caller's access to `case_id` itself is verified by the gateway first.
    """
    conditions = [KbChunk.organization_id == ctx.organization_id]
    if case_id is not None:
        conditions.append((KbChunk.case_id == case_id) | (KbChunk.case_id.is_(None)))
    else:
        conditions.append(KbChunk.case_id.is_(None))

    rows = db.scalars(select(KbChunk).where(*conditions)).all()
    if not rows:
        return []

    query_emb = get_provider().embed([query])[0]
    doc_refs = {
        d.id: d.source_ref
        for d in db.scalars(
            select(KbDocument).where(KbDocument.organization_id == ctx.organization_id)
        ).all()
    }

    scored = [
        RetrievedChunk(
            chunk_id=c.id,
            kb_document_id=c.kb_document_id,
            case_id=c.case_id,
            text=c.text,
            score=_cosine(query_emb, c.embedding_json),
            source_ref=doc_refs.get(c.kb_document_id),
        )
        for c in rows
    ]
    scored.sort(key=lambda r: r.score, reverse=True)
    return scored[:top_k]
