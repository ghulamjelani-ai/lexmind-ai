"""Client management: CRUD + conflict-of-interest checking."""

from __future__ import annotations

import uuid
from datetime import UTC

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.crypto import encrypt_str
from app.core.rbac import AuthContext
from app.models.case import Case
from app.models.client import Client
from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
    ConflictMatch,
    ConflictResult,
)


def create_client(db: Session, ctx: AuthContext, data: ClientCreate) -> Client:
    client = Client(
        organization_id=ctx.organization_id,
        full_name=data.full_name,
        cnic_enc=encrypt_str(data.cnic) if data.cnic else None,
        email=str(data.email) if data.email else None,
        phone=data.phone,
        address=data.address,
        assigned_lawyer_id=data.assigned_lawyer_id,
        created_by=ctx.user_id,
    )
    db.add(client)
    db.flush()
    return client


def get_client(db: Session, ctx: AuthContext, client_id: uuid.UUID) -> Client | None:
    return db.scalar(
        select(Client).where(
            Client.id == client_id,
            Client.organization_id == ctx.organization_id,
            Client.deleted_at.is_(None),
        )
    )


def list_clients(
    db: Session, ctx: AuthContext, *, q: str | None, limit: int, offset: int
) -> tuple[list[Client], int]:
    conditions = [
        Client.organization_id == ctx.organization_id,
        Client.deleted_at.is_(None),
    ]
    if q:
        conditions.append(Client.full_name.ilike(f"%{q}%"))

    total = db.scalar(select(func.count()).select_from(Client).where(*conditions)) or 0
    rows = list(
        db.scalars(
            select(Client).where(*conditions).order_by(Client.full_name).limit(limit).offset(offset)
        ).all()
    )
    return rows, total


def update_client(db: Session, client: Client, data: ClientUpdate) -> Client:
    patch = data.model_dump(exclude_unset=True)
    if "cnic" in patch:
        cnic = patch.pop("cnic")
        client.cnic_enc = encrypt_str(cnic) if cnic else None
    if "email" in patch and patch["email"] is not None:
        patch["email"] = str(patch["email"])
    for field, value in patch.items():
        setattr(client, field, value)
    db.flush()
    return client


def soft_delete_client(db: Session, client: Client) -> None:
    from datetime import datetime

    client.deleted_at = datetime.now(tz=UTC)
    db.flush()


def check_conflict(db: Session, ctx: AuthContext, name: str) -> ConflictResult:
    """Flag a potential conflict of interest: the name already exists as a
    client, or appears as an opposing party in an existing case."""
    matches: list[ConflictMatch] = []

    for c in db.scalars(
        select(Client).where(
            Client.organization_id == ctx.organization_id,
            Client.deleted_at.is_(None),
            Client.full_name.ilike(f"%{name}%"),
        )
    ).all():
        matches.append(
            ConflictMatch(kind="existing_client", reference_id=c.id, label=c.full_name)
        )

    for case in db.scalars(
        select(Case).where(
            Case.organization_id == ctx.organization_id,
            Case.deleted_at.is_(None),
            Case.opposite_party.ilike(f"%{name}%"),
        )
    ).all():
        matches.append(
            ConflictMatch(
                kind="opposing_party",
                reference_id=case.id,
                label=f"Opposing party in: {case.title}",
            )
        )

    return ConflictResult(name=name, has_conflict=bool(matches), matches=matches)
