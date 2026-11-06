"""Tasks. A user sees tasks they created or are assigned; broad scopes see all."""

from __future__ import annotations

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.rbac import SCOPE_ALL, AuthContext
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def _sees_all(ctx: AuthContext) -> bool:
    return (
        ctx.scope_for("tasks:create") == SCOPE_ALL
        or ctx.scope_for("tasks:update") == SCOPE_ALL
    )


def create_task(db: Session, ctx: AuthContext, data: TaskCreate) -> Task:
    task = Task(
        organization_id=ctx.organization_id,
        case_id=data.case_id,
        title=data.title,
        description=data.description,
        assignee_id=data.assignee_id or ctx.user_id,
        due_at=data.due_at,
        created_by=ctx.user_id,
    )
    db.add(task)
    db.flush()
    return task


def get_task(db: Session, ctx: AuthContext, task_id: uuid.UUID) -> Task | None:
    task = db.scalar(
        select(Task).where(Task.id == task_id, Task.organization_id == ctx.organization_id)
    )
    if task is None:
        return None
    if _sees_all(ctx) or task.assignee_id == ctx.user_id or task.created_by == ctx.user_id:
        return task
    return None


def list_tasks(
    db: Session,
    ctx: AuthContext,
    *,
    status: str | None = None,
    case_id: uuid.UUID | None = None,
    mine: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Task], int]:
    conditions = [Task.organization_id == ctx.organization_id]
    if not _sees_all(ctx) or mine:
        conditions.append(or_(Task.assignee_id == ctx.user_id, Task.created_by == ctx.user_id))
    if status:
        conditions.append(Task.status == status)
    if case_id:
        conditions.append(Task.case_id == case_id)

    total = db.scalar(select(func.count()).select_from(Task).where(*conditions)) or 0
    rows = list(
        db.scalars(
            select(Task).where(*conditions).order_by(Task.created_at.desc()).limit(limit).offset(offset)
        ).all()
    )
    return rows, total


def update_task(db: Session, task: Task, data: TaskUpdate) -> Task:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.flush()
    return task
