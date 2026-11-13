from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from pydantic import BaseModel, Field

from app.api.deps import get_tenant_db, require, require_not_restricted
from app.core.rbac import AuthContext
from app.models.finance import Invoice
from app.models.organization import Organization
from app.schemas.finance import (
    ExpenseIn,
    ExpenseOut,
    FinanceSummaryOut,
    InvoiceCreate,
    InvoiceDetailOut,
    InvoiceItemOut,
    InvoiceOut,
    PaymentIn,
    PaymentOut,
    TrustBalanceOut,
    TrustIn,
    TrustTxnOut,
)
from app.services import finance_service, recurring_service
from app.services.finance_service import FinanceError

router = APIRouter(prefix="/finance", tags=["finance"])
_GATE = "clients:manage"


class RecurringCreate(BaseModel):
    client_id: uuid.UUID
    description: str = Field(min_length=1, max_length=300)
    unit_amount: int = Field(ge=0)  # paisa
    quantity: int = Field(default=1, ge=1)
    interval_days: int = Field(default=30, ge=1, le=366)


def _org(db: Session, ctx: AuthContext) -> Organization:
    org = db.get(Organization, ctx.organization_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


def _base_fields(inv: Invoice, total: int, paid: int) -> dict:
    return {
        "id": inv.id,
        "number": inv.number,
        "client_id": inv.client_id,
        "case_id": inv.case_id,
        "status": inv.status,
        "currency": inv.currency,
        "issued_on": inv.issued_on,
        "due_on": inv.due_on,
        "notes": inv.notes,
        "created_at": inv.created_at,
        "total": total,
        "paid": paid,
        "balance": total - paid,
    }


def _out(db: Session, inv: Invoice) -> InvoiceOut:
    total = finance_service.invoice_total(db, inv.id)
    paid = finance_service.invoice_paid(db, inv.id)
    return InvoiceOut(**_base_fields(inv, total, paid))


def _detail(db: Session, inv: Invoice) -> InvoiceDetailOut:
    total = finance_service.invoice_total(db, inv.id)
    paid = finance_service.invoice_paid(db, inv.id)
    return InvoiceDetailOut(
        **_base_fields(inv, total, paid),
        items=[InvoiceItemOut.model_validate(i) for i in finance_service.items_for(db, inv.id)],
        payments=[PaymentOut.model_validate(p) for p in finance_service.payments_for(db, inv.id)],
    )


def _load(db: Session, ctx: AuthContext, invoice_id: uuid.UUID) -> Invoice:
    inv = finance_service.get_invoice(db, ctx, invoice_id)
    if inv is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv


# --- summary -----------------------------------------------------------------
@router.get("/summary", response_model=FinanceSummaryOut)
def summary(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require(_GATE)),
) -> FinanceSummaryOut:
    return FinanceSummaryOut(**finance_service.summary(db, ctx))


# --- invoices ----------------------------------------------------------------
@router.post(
    "/invoices",
    response_model=InvoiceDetailOut,
    status_code=201,
    dependencies=[Depends(require_not_restricted)],
)
def create_invoice(
    body: InvoiceCreate,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require(_GATE)),
) -> InvoiceDetailOut:
    inv = finance_service.create_invoice(db, ctx, body.model_dump())
    db.commit()
    db.refresh(inv)
    return _detail(db, inv)


@router.get("/invoices", response_model=list[InvoiceOut])
def list_invoices(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require(_GATE)),
    status_: str | None = Query(default=None, alias="status"),
) -> list[InvoiceOut]:
    return [_out(db, i) for i in finance_service.list_invoices(db, ctx, status=status_)]


@router.get("/invoices/{invoice_id}", response_model=InvoiceDetailOut)
def get_invoice(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require(_GATE)),
) -> InvoiceDetailOut:
    return _detail(db, _load(db, ctx, invoice_id))


@router.post("/invoices/{invoice_id}/send", response_model=InvoiceOut)
def send_invoice(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require(_GATE)),
) -> InvoiceOut:
    inv = finance_service.send_invoice(db, _load(db, ctx, invoice_id))
    db.commit()
    db.refresh(inv)
    return _out(db, inv)


@router.post("/invoices/{invoice_id}/void", response_model=InvoiceOut)
def void_invoice(
    invoice_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require(_GATE)),
) -> InvoiceOut:
    inv = finance_service.void_invoice(db, _load(db, ctx, invoice_id))
    db.commit()
    db.refresh(inv)
    return _out(db, inv)


@router.post("/invoices/{invoice_id}/payments", response_model=InvoiceDetailOut, status_code=201)
def record_payment(
    invoice_id: uuid.UUID,
    body: PaymentIn,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require(_GATE)),
) -> InvoiceDetailOut:
    inv = _load(db, ctx, invoice_id)
    try:
        finance_service.record_payment(db, ctx, inv, body.model_dump())
    except FinanceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    db.commit()
    db.refresh(inv)
    return _detail(db, inv)


# --- expenses ----------------------------------------------------------------
@router.post("/expenses", response_model=ExpenseOut, status_code=201)
def record_expense(
    body: ExpenseIn,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require(_GATE)),
) -> ExpenseOut:
    exp = finance_service.record_expense(db, ctx, body.model_dump())
    db.commit()
    db.refresh(exp)
    return ExpenseOut.model_validate(exp)


@router.get("/expenses", response_model=list[ExpenseOut])
def list_expenses(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require(_GATE)),
) -> list[ExpenseOut]:
    return [ExpenseOut.model_validate(e) for e in finance_service.list_expenses(db, ctx)]


# --- trust accounting --------------------------------------------------------
@router.post("/trust", response_model=TrustTxnOut, status_code=201)
def trust_txn(
    body: TrustIn,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require(_GATE)),
) -> TrustTxnOut:
    try:
        txn = finance_service.trust_transaction(db, ctx, body.model_dump())
    except FinanceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    db.commit()
    db.refresh(txn)
    return TrustTxnOut.model_validate(txn)


@router.get("/trust/{client_id}", response_model=TrustBalanceOut)
def trust_balance(
    client_id: uuid.UUID,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require(_GATE)),
) -> TrustBalanceOut:
    return TrustBalanceOut(
        client_id=client_id,
        balance=finance_service.trust_balance(db, ctx, client_id),
        transactions=[
            TrustTxnOut.model_validate(t) for t in finance_service.trust_ledger(db, ctx, client_id)
        ],
    )


# --- recurring invoices (retainers) ------------------------------------------
@router.get("/recurring")
def list_recurring(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require(_GATE)),
) -> list[dict]:
    return recurring_service.list_templates(_org(db, ctx))


@router.post("/recurring")
def create_recurring(
    body: RecurringCreate,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require(_GATE)),
) -> dict:
    tpl = recurring_service.add_template(
        db, _org(db, ctx),
        client_id=str(body.client_id),
        description=body.description,
        unit_amount=body.unit_amount,
        quantity=body.quantity,
        interval_days=body.interval_days,
    )
    db.commit()
    return tpl


@router.delete("/recurring/{template_id}", status_code=204)
def delete_recurring(
    template_id: str,
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require(_GATE)),
) -> None:
    if not recurring_service.remove_template(db, _org(db, ctx), template_id):
        raise HTTPException(status_code=404, detail="Template not found")
    db.commit()


@router.post("/recurring/run", dependencies=[Depends(require_not_restricted)])
def run_recurring(
    db: Session = Depends(get_tenant_db),
    ctx: AuthContext = Depends(require(_GATE)),
) -> dict:
    result = recurring_service.run_due(db, ctx, _org(db, ctx))
    db.commit()
    return result
