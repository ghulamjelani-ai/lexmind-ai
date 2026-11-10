"""Finance & trust accounting.

Money is stored as integer MINOR UNITS (paisa) — never floats — so totals are
exact. Derived figures (invoice totals, amounts paid, trust balances) are
computed from rows, not cached, so they can never drift. Client trust money is
tracked in a separate ledger that can never go negative (enforced in the
service), which is the lawyer-specific accounting rule generic billing tools miss.
"""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import BigInteger, Boolean, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import GUID, Base, TenantMixin, TimestampMixin, UUIDMixin


class Invoice(UUIDMixin, TimestampMixin, TenantMixin, Base):
    __tablename__ = "invoices"

    number: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    client_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("clients.id", ondelete="CASCADE"), index=True, nullable=False
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("cases.id", ondelete="SET NULL"), index=True, nullable=True
    )
    # draft | sent | partial | paid | void
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="PKR", nullable=False)
    issued_on: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    due_on: Mapped[date | None] = mapped_column(Date, index=True, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)


class InvoiceItem(UUIDMixin, TimestampMixin, TenantMixin, Base):
    __tablename__ = "invoice_items"

    invoice_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("invoices.id", ondelete="CASCADE"), index=True, nullable=False
    )
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    quantity: Mapped[int] = mapped_column(BigInteger, default=1, nullable=False)
    unit_amount: Mapped[int] = mapped_column(BigInteger, nullable=False)  # paisa
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)  # quantity * unit_amount


class Payment(UUIDMixin, TimestampMixin, TenantMixin, Base):
    __tablename__ = "payments"

    invoice_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("invoices.id", ondelete="CASCADE"), index=True, nullable=False
    )
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)  # paisa
    method: Mapped[str] = mapped_column(String(20), default="cash", nullable=False)
    paid_on: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    note: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)


class Expense(UUIDMixin, TimestampMixin, TenantMixin, Base):
    __tablename__ = "expenses"

    case_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("cases.id", ondelete="SET NULL"), index=True, nullable=True
    )
    client_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("clients.id", ondelete="SET NULL"), index=True, nullable=True
    )
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)  # paisa
    incurred_on: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    billable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    note: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)


class TrustTransaction(UUIDMixin, TimestampMixin, TenantMixin, Base):
    """Client trust (retainer) money ledger. Balance = deposits - withdrawals,
    enforced non-negative by the service."""

    __tablename__ = "trust_transactions"

    client_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("clients.id", ondelete="CASCADE"), index=True, nullable=False
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("cases.id", ondelete="SET NULL"), nullable=True
    )
    kind: Mapped[str] = mapped_column(String(12), nullable=False)  # deposit | withdrawal
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)  # paisa, always positive
    balance_after: Mapped[int] = mapped_column(BigInteger, nullable=False)  # snapshot for audit
    note: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
