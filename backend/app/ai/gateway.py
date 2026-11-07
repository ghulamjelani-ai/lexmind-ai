"""The single entry point to the AI subsystem.

Every AI request goes through here so that, in one place, we:
  1. enforce the caller's authorization (which case/docs they may use as context),
  2. retrieve only authorized grounding chunks,
  3. sandbox untrusted content (prompt-injection defense),
  4. call the configured provider,
  5. attach source citations and audit the run.
Controllers never call a provider directly.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai import retrieval
from app.ai.providers import get_provider
from app.ai.providers.base import ChatMessage
from app.ai.sandbox import SYSTEM_GROUNDING, wrap_untrusted
from app.core.config import get_settings
from app.core.rbac import AuthContext
from app.models.case import Case
from app.services import audit_service, case_service


class AiAuthorizationError(Exception):
    pass


@dataclass
class AiAnswer:
    content: str
    citations: list[dict] = field(default_factory=list)


def ask(
    db: Session,
    ctx: AuthContext,
    *,
    question: str,
    mode: str = "general",
    case_id: uuid.UUID | None = None,
) -> AiAnswer:
    settings = get_settings()

    # 1. Authorization: case mode requires access to that specific case.
    if mode == "case":
        if case_id is None:
            raise AiAuthorizationError("case mode requires a case_id")
        case = db.scalar(
            select(Case).where(
                Case.id == case_id,
                Case.organization_id == ctx.organization_id,
                Case.deleted_at.is_(None),
            )
        )
        if case is None or not case_service.can_access(db, ctx, case, "cases:read"):
            raise AiAuthorizationError("Not authorized for this case")
    else:
        case_id = None  # general mode never reads case documents

    # 2. Retrieve only authorized grounding chunks.
    chunks = retrieval.retrieve(
        db, ctx, question, case_id=case_id, top_k=settings.ai_retrieval_top_k
    )

    # 3. Build the prompt: fixed system instruction + sandboxed data blocks.
    system = SYSTEM_GROUNDING
    if chunks:
        blocks = "\n\n".join(
            wrap_untrusted(f"CONTEXT {i + 1}", c.text) for i, c in enumerate(chunks)
        )
        system = f"{system}\n\n{blocks}"
    messages = [ChatMessage("system", system), ChatMessage("user", question)]

    # 4. Provider call.
    answer = get_provider().chat(messages)

    # 5. Citations (internal KB chunks are 'unverified' — not official sources).
    citations = [
        {
            "chunk_id": str(c.chunk_id),
            "source_ref": c.source_ref,
            "quoted_text": c.text[:200],
            "verification_status": "unverified",
        }
        for c in chunks
    ]

    audit_service.record(
        db,
        action="ai.ask",
        result="allow",
        organization_id=ctx.organization_id,
        actor_id=ctx.user_id,
        resource_type="case" if mode == "case" else None,
        resource_id=str(case_id) if case_id else None,
        metadata={"mode": mode, "provider": get_provider().name, "chunks": len(chunks)},
    )
    return AiAnswer(content=answer, citations=citations)
