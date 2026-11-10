"""Finance & trust accounting service.

All money is integer paisa. Invoice totals and amounts paid are computed from
child rows every time (never cached), and the client trust balance is enforced
to stay >= 0. These are deterministic accounting rules — no AI, no estimates.
"""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.core.rbac import AuthContext
from app.models.finance import Expense, Invoice, InvoiceItem, Payment, TrustTransaction
from app.services import audit_service


class FinanceError(ValueError):
    """Raised for an accounting rule violation (e.g. overdrawing trust)."""


# --- helpers -----------------------------------------------------------------
def _next_invoice_number(db: Session, ctx: AuthContext) -> str:
    count = db.scalar(
        select(func.count()).select_from(Invoice).where(
            Invoice.organization_id == ctx.organization_id
        )
    ) or 0
    return f"INV-{count + 1:05d}"


def invoice_total(db: Session, invoice_id: uuid.UUID) -> int:
    return db.scalar(
        select(func.coalesce(func.sum(InvoiceItem.amount), 0)).where(
            InvoiceItem.invoice_id == invoice_id
        )
    ) or 0


def invoice_paid(db: Session, invoice_id: uuid.UUID) -> int:
    return db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.invoice_id == invoice_id
        )
    ) or 0


def _refresh_status(db: Session, invoice: Invoice) -> None:
    """Derive paid/partial/sent from the amounts — void and draft are manual."""
    if invoice.status in ("void", "draft"):
        return
    total = invoice_total(db, invoice.id)
    paid = invoice_paid(db, invoice.id)
    if total > 0 and paid >= total:
        invoice.status = "paid"
    elif paid > 0:
        invoice.status = "partial"
    else:
        invoice.status = "sent"


# --- invoices ----------------------------------------------------------------
def create_invoice(db: Session, ctx: AuthContext, data: dict) -> Invoice:
    invoice = Invoice(
        organization_id=ctx.organization_id,
        number=_next_invoice_number(db, ctx),
        client_id=data["client_id"],
        case_id=data.get("case_id"),
        currency=data.get("currency", "PKR"),
        due_on=data.get("due_on"),
        notes=data.get("notes"),
        status="draft",
        created_by=ctx.user_id,
    )
    db.add(invoice)
    db.flush()
    for item in data.get("items", []):
        qty = int(item.get("quantity", 1))
        unit = int(item["unit_amount"])
        db.add(
            InvoiceItem(
                organization_id=ctx.organization_id,
                invoice_id=invoice.id,
                description=item["description"],
                quantity=qty,
                unit_amount=unit,
                amount=qty * unit,
            )
        )
    db.flush()
    return invoice


def send_invoice(db: Session, invoice: Invoice) -> Invoice:
    if invoice.status == "draft":
        invoice.status = "sent"
    db.flush()
    return invoice


def void_invoice(db: Session, invoice: Invoice) -> Invoice:
    invoice.status = "void"
    db.flush()
    return invoice


def get_invoice(db: Session, ctx: AuthContext, invoice_id: uuid.UUID) -> Invoice | None:
    return db.scalar(
        select(Invoice).where(
            Invoice.id == invoice_id, Invoice.organization_id == ctx.organization_id
        )
    )


def list_invoices(db: Session, ctx: AuthContext, *, status: str | None = None) -> list[Invoice]:
    conds = [Invoice.organization_id == ctx.organization_id]
    if status:
        conds.append(Invoice.status == status)
    return list(
        db.scalars(select(Invoice).where(*conds).order_by(Invoice.created_at.desc())).all()
    )


def items_for(db: Session, invoice_id: uuid.UUID) -> list[InvoiceItem]:
    return list(db.scalars(select(InvoiceItem).where(InvoiceItem.invoice_id == invoice_id)).all())


def payments_for(db: Session, invoice_id: uuid.UUID) -> list[Payment]:
    return list(
        db.scalars(
            select(Payment).where(Payment.invoice_id == invoice_id).order_by(Payment.paid_on)
        ).all()
    )


def record_payment(db: Session, ctx: AuthContext, invoice: Invoice, data: dict) -> Payment:
    amount = int(data["amount"])
    if amount <= 0:
        raise FinanceError("Payment amount must be positive.")
    if invoice.status == "void":
        raise FinanceError("Cannot record a payment against a void invoice.")
    outstanding = invoice_total(db, invoice.id) - invoice_paid(db, invoice.id)
    if amount > outstanding:
        raise FinanceError(
            f"Payment exceeds the outstanding balance ({outstanding} paisa)."
        )
    method = data.get("method", "cash")
    # Paying from trust draws down the client's trust ledger (never below zero).
    if method == "trust":
        _trust_apply(
            db, ctx, client_id=invoice.client_id, case_id=invoice.case_id, amount=amount,
            note=f"Applied to invoice {invoice.number}",
        )
    payment = Payment(
        organization_id=ctx.organization_id,
        invoice_id=invoice.id,
        amount=amount,
        method=method,
        paid_on=data.get("paid_on") or date.today(),
        note=data.get("note"),
        created_by=ctx.user_id,
    )
    db.add(payment)
    db.flush()
    _refresh_status(db, invoice)
    audit_service.record(
        db,
        action="finance.payment_recorded",
        organization_id=ctx.organization_id,
        actor_id=ctx.user_id,
        resource_type="invoice",
        resource_id=str(invoice.id),
        metadata={"amount": amount, "method": method},
    )
    db.flush()
    return payment


# --- expenses ----------------------------------------------------------------
def record_expense(db: Session, ctx: AuthContext, data: dict) -> Expense:
    exp = Expense(
        organization_id=ctx.organization_id,
        case_id=data.get("case_id"),
        client_id=data.get("client_id"),
        description=data["description"],
        amount=int(data["amount"]),
        incurred_on=data.get("incurred_on") or date.today(),
        billable=bool(data.get("billable", True)),
        note=data.get("note"),
        created_by=ctx.user_id,
    )
    db.add(exp)
    db.flush()
    return exp


def list_expenses(db: Session, ctx: AuthContext) -> list[Expense]:
    return list(
        db.scalars(
            select(Expense)
            .where(Expense.organization_id == ctx.organization_id)
            .order_by(Expense.incurred_on.desc())
        ).all()
    )


# --- trust accounting --------------------------------------------------------
def trust_balance(db: Session, ctx: AuthContext, client_id: uuid.UUID) -> int:
    deposits = db.scalar(
        select(func.coalesce(func.sum(TrustTransaction.amount), 0)).where(
            TrustTransaction.organization_id == ctx.organization_id,
            TrustTransaction.client_id == client_id,
            TrustTransaction.kind == "deposit",
        )
    ) or 0
    withdrawals = db.scalar(
        select(func.coalesce(func.sum(TrustTransaction.amount), 0)).where(
            TrustTransaction.organization_id == ctx.organization_id,
            TrustTransaction.client_id == client_id,
            TrustTransaction.kind == "withdrawal",
        )
    ) or 0
    return int(deposits) - int(withdrawals)


def _trust_apply(
    db: Session,
    ctx: AuthContext,
    *,
    client_id: uuid.UUID,
    amount: int,
    note: str | None,
    case_id: uuid.UUID | None = None,
) -> TrustTransaction:
    """A withdrawal from trust — enforced to never overdraw."""
    balance = trust_balance(db, ctx, client_id)
    if amount > balance:
        raise FinanceError(
            f"Trust withdrawal exceeds the client's trust balance ({balance} paisa)."
        )
    txn = TrustTransaction(
        organization_id=ctx.organization_id,
        client_id=client_id,
        case_id=case_id,
        kind="withdrawal",
        amount=amount,
        balance_after=balance - amount,
        note=note,
        created_by=ctx.user_id,
    )
    db.add(txn)
    db.flush()
    return txn


def trust_transaction(db: Session, ctx: AuthContext, data: dict) -> TrustTransaction:
    kind = data["kind"]
    amount = int(data["amount"])
    client_id = data["client_id"]
    if amount <= 0:
        raise FinanceError("Amount must be positive.")
    if kind == "withdrawal":
        return _trust_apply(
            db, ctx, client_id=client_id, amount=amount, note=data.get("note"),
            case_id=data.get("case_id"),
        )
    if kind != "deposit":
        raise FinanceError("kind must be 'deposit' or 'withdrawal'.")
    balance = trust_balance(db, ctx, client_id)
    txn = TrustTransaction(
        organization_id=ctx.organization_id,
        client_id=client_id,
        case_id=data.get("case_id"),
        kind="deposit",
        amount=amount,
        balance_after=balance + amount,
        note=data.get("note"),
        created_by=ctx.user_id,
    )
    db.add(txn)
    db.flush()
    return txn


def trust_ledger(db: Session, ctx: AuthContext, client_id: uuid.UUID) -> list[TrustTransaction]:
    return list(
        db.scalars(
            select(TrustTransaction)
            .where(
                TrustTransaction.organization_id == ctx.organization_id,
                TrustTransaction.client_id == client_id,
            )
            .order_by(TrustTransaction.created_at.desc())
        ).all()
    )


# --- summary -----------------------------------------------------------------
def summary(db: Session, ctx: AuthContext, *, today: date | None = None) -> dict:
    today = today or date.today()
    invoices = list_invoices(db, ctx)
    total_invoiced = 0
    total_paid = 0
    outstanding = 0
    overdue = 0
    for inv in invoices:
        if inv.status == "void":
            continue
        t = invoice_total(db, inv.id)
        p = invoice_paid(db, inv.id)
        total_invoiced += t
        total_paid += p
        bal = t - p
        outstanding += bal
        if bal > 0 and inv.due_on and inv.due_on < today and inv.status != "paid":
            overdue += 1

    trust_total = db.scalar(
        select(
            func.coalesce(
                func.sum(
                    case(
                        (TrustTransaction.kind == "deposit", TrustTransaction.amount),
                        else_=-TrustTransaction.amount,
                    )
                ),
                0,
            )
        ).where(TrustTransaction.organization_id == ctx.organization_id)
    ) or 0
    expenses_total = db.scalar(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.organization_id == ctx.organization_id
        )
    ) or 0

    return {
        "currency": "PKR",
        "total_invoiced": int(total_invoiced),
        "total_paid": int(total_paid),
        "outstanding": int(outstanding),
        "overdue_invoices": int(overdue),
        "trust_balance": int(trust_total),
        "expenses_total": int(expenses_total),
        "invoice_count": len(invoices),
        "as_of": today.isoformat(),
    }
