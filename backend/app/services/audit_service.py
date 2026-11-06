"""Append-only audit logging helper."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def record(
    db: Session,
    *,
    action: str,
    result: str = "allow",
    organization_id: uuid.UUID | None = None,
    actor_id: uuid.UUID | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
    metadata: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            organization_id=organization_id,
            actor_id=actor_id,
            action=action,
            result=result,
            resource_type=resource_type,
            resource_id=resource_id,
            ip=ip,
            user_agent=(user_agent or "")[:512] or None,
            metadata_json=metadata or {},
        )
    )
    db.flush()
