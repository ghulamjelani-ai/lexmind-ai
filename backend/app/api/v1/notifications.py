from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_auth_context, get_tenant_db
from app.core.rbac import AuthContext
from app.schemas.common import Page
from app.schemas.notification import NotificationOut
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=Page[NotificationOut])
def list_notifications(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(get_auth_context),
    unread: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> Page[NotificationOut]:
    rows, total = notification_service.list_for_user(
        db, ctx, unread_only=unread, limit=limit, offset=offset
    )
    return Page[NotificationOut](
        items=[NotificationOut.model_validate(n) for n in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_tenant_db), ctx: AuthContext = Depends(get_auth_context)
) -> dict[str, int]:
    return {"unread": notification_service.unread_count(db, ctx)}


@router.post("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_read(
    notification_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> None:
    if not notification_service.mark_read(db, ctx, notification_id):
        raise HTTPException(status_code=404, detail="Notification not found")
    db.commit()


@router.post("/read-all")
def mark_all_read(
    db: Session = Depends(get_tenant_db), ctx: AuthContext = Depends(get_auth_context)
) -> dict[str, int]:
    n = notification_service.mark_all_read(db, ctx)
    db.commit()
    return {"marked_read": n}
