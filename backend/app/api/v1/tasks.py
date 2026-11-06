from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_auth_context, get_tenant_db, require
from app.core.rbac import AuthContext
from app.schemas.common import Page
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    body: TaskCreate,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("tasks:create")),
) -> TaskOut:
    task = task_service.create_task(db, ctx, body)
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)


@router.get("", response_model=Page[TaskOut])
def list_tasks(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(get_auth_context),
    status_: str | None = Query(default=None, alias="status"),
    case_id: uuid.UUID | None = Query(default=None),
    mine: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> Page[TaskOut]:
    rows, total = task_service.list_tasks(
        db, ctx, status=status_, case_id=case_id, mine=mine, limit=limit, offset=offset
    )
    return Page[TaskOut](
        items=[TaskOut.model_validate(t) for t in rows], total=total, limit=limit, offset=offset
    )


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> TaskOut:
    task = task_service.get_task(db, ctx, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskOut.model_validate(task)


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: uuid.UUID,
    body: TaskUpdate,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("tasks:update")),
) -> TaskOut:
    task = task_service.get_task(db, ctx, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task = task_service.update_task(db, task, body)
    db.commit()
    db.refresh(task)
    return TaskOut.model_validate(task)
