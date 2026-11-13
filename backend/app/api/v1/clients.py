from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_tenant_db, require, require_not_restricted
from app.core.rbac import AuthContext
from app.schemas.client import (
    ClientCreate,
    ClientOut,
    ClientUpdate,
    ConflictResult,
)
from app.schemas.common import Page
from app.services import client_service

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post(
    "",
    response_model=ClientOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_not_restricted)],
)
def create_client(
    body: ClientCreate,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("clients:manage")),
) -> ClientOut:
    client = client_service.create_client(db, ctx, body)
    db.commit()
    db.refresh(client)
    return ClientOut.model_validate(client)


@router.get("", response_model=Page[ClientOut])
def list_clients(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("clients:manage")),
    q: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> Page[ClientOut]:
    rows, total = client_service.list_clients(db, ctx, q=q, limit=limit, offset=offset)
    return Page[ClientOut](
        items=[ClientOut.model_validate(c) for c in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/conflict-check", response_model=ConflictResult)
def conflict_check(
    name: str = Query(min_length=1),
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("clients:manage")),
) -> ConflictResult:
    return client_service.check_conflict(db, ctx, name)


@router.get("/{client_id}", response_model=ClientOut)
def get_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("clients:manage")),
) -> ClientOut:
    client = client_service.get_client(db, ctx, client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return ClientOut.model_validate(client)


@router.patch("/{client_id}", response_model=ClientOut)
def update_client(
    client_id: uuid.UUID,
    body: ClientUpdate,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("clients:manage")),
) -> ClientOut:
    client = client_service.get_client(db, ctx, client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    client = client_service.update_client(db, client, body)
    db.commit()
    db.refresh(client)
    return ClientOut.model_validate(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("clients:manage")),
) -> None:
    client = client_service.get_client(db, ctx, client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    client_service.soft_delete_client(db, client)
    db.commit()
