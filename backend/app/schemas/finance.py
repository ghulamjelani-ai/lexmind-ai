from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


# --- invoices ----------------------------------------------------------------
class InvoiceItemIn(BaseModel):
    description: str = Field(min_length=1, max_length=300)
    quantity: int = Field(default=1, ge=1)
    unit_amount: int = Field(ge=0)  # paisa


class InvoiceCreate(BaseModel):
    client_id: uuid.UUID
    case_id: uuid.UUID | None = None
    due_on: date | None = None
    currency: str = Field(default="PKR", max_length=3)
    notes: str | None = Field(default=None, max_length=2000)
    items: list[InvoiceItemIn] = []


class InvoiceItemOut(BaseModel):
    id: uuid.UUID
    description: str
    quantity: int
    unit_amount: int
    amount: int

    model_config = {"from_attributes": True}


class PaymentIn(BaseModel):
    amount: int = Field(gt=0)  # paisa
    method: str = Field(default="cash", max_length=20)
    paid_on: date | None = None
    note: str | None = Field(default=None, max_length=300)


class PaymentOut(BaseModel):
    id: uuid.UUID
    amount: int
    method: str
    paid_on: date
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class InvoiceOut(BaseModel):
    id: uuid.UUID
    number: str
    client_id: uuid.UUID
    case_id: uuid.UUID | None
    status: str
    currency: str
    issued_on: date
    due_on: date | None
    notes: str | None
    created_at: datetime
    # computed
    total: int
    paid: int
    balance: int

    model_config = {"from_attributes": True}


class InvoiceDetailOut(InvoiceOut):
    items: list[InvoiceItemOut] = []
    payments: list[PaymentOut] = []


# --- expenses ----------------------------------------------------------------
class ExpenseIn(BaseModel):
    description: str = Field(min_length=1, max_length=300)
    amount: int = Field(gt=0)
    case_id: uuid.UUID | None = None
    client_id: uuid.UUID | None = None
    incurred_on: date | None = None
    billable: bool = True
    note: str | None = Field(default=None, max_length=300)


class ExpenseOut(BaseModel):
    id: uuid.UUID
    description: str
    amount: int
    case_id: uuid.UUID | None
    client_id: uuid.UUID | None
    incurred_on: date
    billable: bool
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- trust -------------------------------------------------------------------
class TrustIn(BaseModel):
    client_id: uuid.UUID
    kind: str = Field(pattern="^(deposit|withdrawal)$")
    amount: int = Field(gt=0)
    case_id: uuid.UUID | None = None
    note: str | None = Field(default=None, max_length=300)


class TrustTxnOut(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    case_id: uuid.UUID | None
    kind: str
    amount: int
    balance_after: int
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TrustBalanceOut(BaseModel):
    client_id: uuid.UUID
    balance: int
    transactions: list[TrustTxnOut]


# --- summary -----------------------------------------------------------------
class FinanceSummaryOut(BaseModel):
    currency: str
    total_invoiced: int
    total_paid: int
    outstanding: int
    overdue_invoices: int
    trust_balance: int
    expenses_total: int
    invoice_count: int
    as_of: str
