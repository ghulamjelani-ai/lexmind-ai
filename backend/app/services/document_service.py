"""Document management: upload, versioning, and private storage.

Bytes are written to object storage (never the DB); each upload records a
checksum and size. Malware scanning (scan_status) and OCR arrive in later phases,
so new documents are scan_status="pending".
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core import constants as C
from app.core.rbac import AuthContext
from app.integrations.storage import get_storage
from app.models.case import CaseEvent
from app.models.document import Document, DocumentVersion


class DocumentError(Exception):
    pass


def _storage_key(org_id: uuid.UUID, doc_id: uuid.UUID, version: int) -> str:
    return f"{org_id}/{doc_id}/v{version}"


def upload(
    db: Session,
    ctx: AuthContext,
    *,
    title: str,
    category: str,
    case_id: uuid.UUID | None,
    mime: str | None,
    data: bytes,
) -> Document:
    if category not in C.DOCUMENT_CATEGORIES:
        raise DocumentError(f"Unknown category '{category}'")

    doc_id = uuid.uuid4()
    key = _storage_key(ctx.organization_id, doc_id, 1)
    checksum = hashlib.sha256(data).hexdigest()
    get_storage().put(key, data)

    doc = Document(
        id=doc_id,
        organization_id=ctx.organization_id,
        case_id=case_id,
        title=title,
        category=category,
        storage_key=key,
        mime=mime,
        size=len(data),
        checksum=checksum,
        scan_status=C.DOC_SCAN_PENDING,
        current_version=1,
        created_by=ctx.user_id,
    )
    db.add(doc)
    db.flush()

    db.add(
        DocumentVersion(
            organization_id=ctx.organization_id,
            document_id=doc.id,
            version_no=1,
            storage_key=key,
            mime=mime,
            size=len(data),
            checksum=checksum,
            created_by=ctx.user_id,
        )
    )
    if case_id is not None:
        db.add(
            CaseEvent(
                organization_id=ctx.organization_id,
                case_id=case_id,
                event_type=C.EVENT_DOCUMENT_UPLOADED,
                actor_id=ctx.user_id,
                payload_json={"document_id": str(doc.id), "title": title},
            )
        )
    db.flush()
    return doc


def add_version(
    db: Session, ctx: AuthContext, doc: Document, *, mime: str | None, data: bytes
) -> Document:
    version = doc.current_version + 1
    key = _storage_key(ctx.organization_id, doc.id, version)
    checksum = hashlib.sha256(data).hexdigest()
    get_storage().put(key, data)

    db.add(
        DocumentVersion(
            organization_id=ctx.organization_id,
            document_id=doc.id,
            version_no=version,
            storage_key=key,
            mime=mime,
            size=len(data),
            checksum=checksum,
            created_by=ctx.user_id,
        )
    )
    doc.current_version = version
    doc.storage_key = key
    doc.mime = mime
    doc.size = len(data)
    doc.checksum = checksum
    doc.scan_status = C.DOC_SCAN_PENDING
    db.flush()
    return doc


def get_document(db: Session, ctx: AuthContext, document_id: uuid.UUID) -> Document | None:
    return db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.organization_id == ctx.organization_id,
            Document.deleted_at.is_(None),
        )
    )


def list_documents(
    db: Session, ctx: AuthContext, *, case_id: uuid.UUID | None, limit: int, offset: int
) -> tuple[list[Document], int]:
    conditions = [
        Document.organization_id == ctx.organization_id,
        Document.deleted_at.is_(None),
    ]
    if case_id:
        conditions.append(Document.case_id == case_id)
    total = db.scalar(select(func.count()).select_from(Document).where(*conditions)) or 0
    rows = list(
        db.scalars(
            select(Document)
            .where(*conditions)
            .order_by(Document.created_at.desc())
            .limit(limit)
            .offset(offset)
        ).all()
    )
    return rows, total


def list_versions(db: Session, doc: Document) -> list[DocumentVersion]:
    return list(
        db.scalars(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == doc.id)
            .order_by(DocumentVersion.version_no.desc())
        ).all()
    )


def read_bytes(doc: Document) -> bytes:
    return get_storage().get(doc.storage_key)


def soft_delete(db: Session, doc: Document) -> None:
    doc.deleted_at = datetime.now(tz=UTC)
    db.flush()
