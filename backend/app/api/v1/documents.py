from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_tenant_db, require
from app.core.config import get_settings
from app.core.rbac import AuthContext
from app.models.case import Case
from app.schemas.common import Page
from app.schemas.document import DocumentOut, DocumentVersionOut
from app.services import case_service, document_service

router = APIRouter(prefix="/documents", tags=["documents"])


def _check_case_access(db: Session, ctx: AuthContext, case_id: uuid.UUID | None) -> None:
    if case_id is None:
        return
    case = db.scalar(
        select(Case).where(
            Case.id == case_id,
            Case.organization_id == ctx.organization_id,
            Case.deleted_at.is_(None),
        )
    )
    if case is None or not case_service.can_access(db, ctx, case, "cases:read"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")


async def _read_upload(file: UploadFile) -> bytes:
    data = await file.read()
    limit = get_settings().max_upload_bytes
    if len(data) > limit:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {limit} byte limit",
        )
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
    return data


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("other"),
    case_id: uuid.UUID | None = Form(default=None),
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("documents:upload")),
) -> DocumentOut:
    _check_case_access(db, ctx, case_id)
    data = await _read_upload(file)
    try:
        doc = document_service.upload(
            db, ctx, title=title, category=category, case_id=case_id,
            mime=file.content_type, data=data,
        )
    except document_service.DocumentError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    db.commit()
    db.refresh(doc)
    return DocumentOut.model_validate(doc)


@router.get("", response_model=Page[DocumentOut])
def list_documents(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("documents:read")),
    case_id: uuid.UUID | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> Page[DocumentOut]:
    rows, total = document_service.list_documents(
        db, ctx, case_id=case_id, limit=limit, offset=offset
    )
    return Page[DocumentOut](
        items=[DocumentOut.model_validate(d) for d in rows], total=total, limit=limit, offset=offset
    )


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("documents:read")),
) -> DocumentOut:
    doc = document_service.get_document(db, ctx, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentOut.model_validate(doc)


@router.get("/{document_id}/download")
def download_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("documents:download")),
) -> Response:
    doc = document_service.get_document(db, ctx, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    data = document_service.read_bytes(doc)
    return Response(
        content=data,
        media_type=doc.mime or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{doc.title}"'},
    )


@router.post("/{document_id}/versions", response_model=DocumentOut)
async def add_version(
    document_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("documents:upload")),
) -> DocumentOut:
    doc = document_service.get_document(db, ctx, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    data = await _read_upload(file)
    doc = document_service.add_version(db, ctx, doc, mime=file.content_type, data=data)
    db.commit()
    db.refresh(doc)
    return DocumentOut.model_validate(doc)


@router.get("/{document_id}/versions", response_model=list[DocumentVersionOut])
def list_versions(
    document_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("documents:read")),
) -> list[DocumentVersionOut]:
    doc = document_service.get_document(db, ctx, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return [DocumentVersionOut.model_validate(v) for v in document_service.list_versions(db, doc)]


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require("documents:upload")),
) -> None:
    doc = document_service.get_document(db, ctx, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    document_service.soft_delete(db, doc)
    db.commit()
