"""Recurring invoices (retainers).

Templates are stored in ``Organization.settings_json["recurring_invoices"]`` (no
schema change). ``run_due`` turns every template that has reached its next run
date into a real draft invoice via ``finance_service`` and advances the schedule.
Amounts are in paisa, consistent with the finance module.
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.core.rbac import AuthContext
from app.models.organization import Organization
from app.services import finance_service

_KEY = "recurring_invoices"


def _today() -> date:
    return datetime.now(UTC).date()


def list_templates(org: Organization) -> list[dict[str, Any]]:
    settings = org.settings_json or {}
    rows = settings.get(_KEY)
    return list(rows) if isinstance(rows, list) else []


def _save(db: Session, org: Organization, rows: list[dict[str, Any]]) -> None:
    settings = dict(org.settings_json or {})
    settings[_KEY] = rows
    org.settings_json = settings
    db.flush()


def add_template(
    db: Session,
    org: Organization,
    *,
    client_id: str,
    description: str,
    unit_amount: int,
    quantity: int = 1,
    interval_days: int = 30,
) -> dict[str, Any]:
    rows = list_templates(org)
    tpl = {
        "id": str(uuid.uuid4()),
        "client_id": str(client_id),
        "description": description,
        "unit_amount": int(unit_amount),
        "quantity": int(quantity),
        "interval_days": int(interval_days),
        "next_run": _today().isoformat(),
        "active": True,
        "created_at": datetime.now(UTC).isoformat(),
    }
    rows.append(tpl)
    _save(db, org, rows)
    return tpl


def remove_template(db: Session, org: Organization, template_id: str) -> bool:
    rows = list_templates(org)
    new = [r for r in rows if r.get("id") != template_id]
    if len(new) == len(rows):
        return False
    _save(db, org, new)
    return True


def run_due(db: Session, ctx: AuthContext, org: Organization, today: date | None = None) -> dict[str, Any]:
    """Generate invoices for every active template whose next_run has arrived,
    then advance each schedule. Returns how many were created."""
    today = today or _today()
    rows = list_templates(org)
    created: list[str] = []
    for tpl in rows:
        if not tpl.get("active", True):
            continue
        try:
            nxt = date.fromisoformat(tpl.get("next_run"))
        except (TypeError, ValueError):
            nxt = today
        if nxt > today:
            continue
        invoice = finance_service.create_invoice(
            db,
            ctx,
            {
                "client_id": uuid.UUID(tpl["client_id"]),
                "due_on": today + timedelta(days=14),
                "notes": "Recurring retainer",
                "items": [
                    {
                        "description": tpl["description"],
                        "quantity": int(tpl.get("quantity", 1)),
                        "unit_amount": int(tpl["unit_amount"]),
                    }
                ],
            },
        )
        created.append(invoice.number)
        tpl["next_run"] = (nxt + timedelta(days=int(tpl.get("interval_days", 30)))).isoformat()
    _save(db, org, rows)
    return {"created": len(created), "invoices": created}
