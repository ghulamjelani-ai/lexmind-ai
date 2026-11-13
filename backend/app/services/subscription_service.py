"""Subscription state and enforcement.

State lives in ``Organization.settings_json["subscription"]`` (no schema change
required). The *effective* status is always recomputed from dates so an expired
trial or an overdue payment is reflected without a background job.

States:
- ``trialing``   — in the free trial window (full Chamber features).
- ``active``     — paid and within the current period.
- ``past_due``   — payment overdue but inside the grace window (still writable).
- ``restricted`` — grace elapsed; paid writes blocked, data kept read-only.
- ``canceled``   — explicitly canceled; treated as restricted.

Billing endpoints stay available in every state so the customer can always pay.
Customer data is never deleted on non-payment.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.core.plans import DEFAULT_PLAN, GRACE_DAYS, TRIAL_DAYS, TRIAL_PLAN, get_plan
from app.models.organization import Organization


def _now() -> datetime:
    return datetime.now(UTC)


def _parse(dt: str | None) -> datetime | None:
    if not dt:
        return None
    try:
        d = datetime.fromisoformat(dt)
        return d if d.tzinfo else d.replace(tzinfo=UTC)
    except ValueError:
        return None


def _default_subscription(org: Organization) -> dict[str, Any]:
    """A fresh org starts on a Chamber-tier trial from its creation date."""
    created = getattr(org, "created_at", None) or _now()
    if created.tzinfo is None:
        created = created.replace(tzinfo=UTC)
    return {
        "plan": org.plan or DEFAULT_PLAN,
        "status": "trialing",
        "trial_ends_at": (created + timedelta(days=TRIAL_DAYS)).isoformat(),
        "current_period_end": None,
        "grace_until": None,
        "last_payment_at": None,
    }


def _raw(org: Organization) -> dict[str, Any]:
    settings = org.settings_json or {}
    sub = settings.get("subscription")
    return dict(sub) if isinstance(sub, dict) else _default_subscription(org)


def effective_status(org: Organization, now: datetime | None = None) -> str:
    """Recompute status from stored state + dates."""
    now = now or _now()
    sub = _raw(org)
    stored = sub.get("status")

    if stored == "canceled":
        return "restricted"

    if stored == "trialing":
        ends = _parse(sub.get("trial_ends_at"))
        if ends and now <= ends:
            return "trialing"
        # trial lapsed without a paid plan → past due, then restricted after grace
        grace = (ends or now) + timedelta(days=GRACE_DAYS)
        return "past_due" if now <= grace else "restricted"

    # paid plans
    period_end = _parse(sub.get("current_period_end"))
    if period_end is None or now <= period_end:
        return "active"
    grace = _parse(sub.get("grace_until")) or (period_end + timedelta(days=GRACE_DAYS))
    return "past_due" if now <= grace else "restricted"


def is_restricted(org: Organization, now: datetime | None = None) -> bool:
    return effective_status(org, now) == "restricted"


def summary(org: Organization, now: datetime | None = None) -> dict[str, Any]:
    """Public view for the billing UI + enforcement."""
    now = now or _now()
    sub = _raw(org)
    status = effective_status(org, now)
    plan_code = sub.get("plan") or org.plan or DEFAULT_PLAN
    plan = get_plan(plan_code)

    # Days left in the relevant window (trial or current period).
    ref = _parse(sub.get("trial_ends_at")) if status == "trialing" else _parse(sub.get("current_period_end"))
    days_left = max(0, (ref - now).days) if ref else None

    return {
        "plan": plan_code,
        "plan_name": plan["name"],
        "price_pkr": plan["price_pkr"],
        "status": status,
        "restricted": status == "restricted",
        "past_due": status == "past_due",
        "trialing": status == "trialing",
        "days_left": days_left,
        "trial_ends_at": sub.get("trial_ends_at"),
        "current_period_end": sub.get("current_period_end"),
        "limits": plan["limits"],
        "features": sorted(plan["features"]),
    }


def set_subscription(db: Session, org: Organization, **fields: Any) -> dict[str, Any]:
    """Merge fields into the stored subscription (reassigns settings_json so
    SQLAlchemy detects the JSON mutation). Keeps org.plan in sync."""
    settings = dict(org.settings_json or {})
    sub = dict(settings.get("subscription") or _default_subscription(org))
    sub.update({k: v for k, v in fields.items() if v is not None or k in sub})
    if "plan" in fields and fields["plan"]:
        org.plan = fields["plan"]
    settings["subscription"] = sub
    org.settings_json = settings
    db.flush()
    return sub


def start_trial_if_absent(db: Session, org: Organization) -> None:
    """Ensure a newly provisioned org has a trial recorded."""
    settings = org.settings_json or {}
    if "subscription" not in settings:
        set_subscription(db, org, **_default_subscription(org))


def mark_paid(db: Session, org: Organization, plan: str, period_days: int = 30) -> dict[str, Any]:
    """Record a successful payment: activate the plan for the next period."""
    now = _now()
    return set_subscription(
        db, org,
        plan=plan,
        status="active",
        current_period_end=(now + timedelta(days=period_days)).isoformat(),
        grace_until=None,
        last_payment_at=now.isoformat(),
    )
