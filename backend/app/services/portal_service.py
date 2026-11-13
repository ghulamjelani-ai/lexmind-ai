"""Client portal data access.

Resolves the *client record* that belongs to a signed-in *client user* and
returns only that client's own cases, invoices and documents. Everything is
scoped to the resolved client's id, so a client can never see another client's
data (on top of the existing org-level RLS).

Linking: a client user is matched to a client record by an explicit
``clients.user_id`` link; if absent, it is auto-linked once by a case-insensitive
email match within the org (only to a record that is not already linked).
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.client import Client
from app.models.document import Document
from app.models.finance import Invoice, InvoiceItem, Payment
from app.models.user import User


def resolve_client(db: Session, user: User) -> Client | None:
    """The client record for this user, auto-linking by email once if needed."""
    linked = db.scalar(
        select(Client).where(Client.user_id == user.id, Client.deleted_at.is_(None))
    )
    if linked is not None:
        return linked

    if user.email:
        match = db.scalar(
            select(Client).where(
                func.lower(Client.email) == user.email.lower(),
                Client.user_id.is_(None),
                Client.deleted_at.is_(None),
            )
        )
        if match is not None:
            match.user_id = user.id  # bind the account to the record
            db.flush()
            return match
    return None


def _invoice_amounts(db: Session, invoice_id) -> tuple[int, int]:
    total = db.scalar(
        select(func.coalesce(func.sum(InvoiceItem.amount), 0)).where(
            InvoiceItem.invoice_id == invoice_id
        )
    ) or 0
    paid = db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.invoice_id == invoice_id)
    ) or 0
    return int(total), int(paid)


def overview(db: Session, user: User) -> dict:
    client = resolve_client(db, user)
    if client is None:
        return {"linked": False, "client": None, "cases": [], "invoices": [], "documents": []}

    cases = db.scalars(
        select(Case).where(Case.client_id == client.id, Case.deleted_at.is_(None))
    ).all()
    case_ids = [c.id for c in cases]
    invoices = db.scalars(
        select(Invoice).where(Invoice.client_id == client.id)
    ).all()
    documents = (
        db.scalars(
            select(Document).where(
                Document.case_id.in_(case_ids), Document.deleted_at.is_(None)
            )
        ).all()
        if case_ids
        else []
    )

    return {
        "linked": True,
        "client": {"id": str(client.id), "full_name": client.full_name, "email": client.email},
        "documents": [
            {"id": str(d.id), "title": d.title, "category": d.category, "created_at": d.created_at.isoformat() if d.created_at else None}
            for d in documents
        ],
        "cases": [
            {
                "id": str(c.id),
                "title": c.title,
                "status": c.status,
                "category": c.category,
                "next_hearing_date": c.next_hearing_date.isoformat() if c.next_hearing_date else None,
            }
            for c in cases
        ],
        "invoices": [
            (lambda total, paid: {
                "id": str(inv.id),
                "number": inv.number,
                "status": inv.status,
                "due_on": inv.due_on.isoformat() if inv.due_on else None,
                "total": total,
                "paid": paid,
                "balance": total - paid,
            })(*_invoice_amounts(db, inv.id))
            for inv in invoices
        ],
    }
