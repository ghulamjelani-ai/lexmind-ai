"""Subscription plan catalogue and entitlements.

Plans mirror the pricing shown on the billing page. Limits are enforced
server-side via ``subscription_service``. Prices are in PKR.
"""

from __future__ import annotations

from typing import Any

# Sentinel for "no limit".
UNLIMITED = -1

PLANS: dict[str, dict[str, Any]] = {
    "free": {
        "code": "free",
        "name": "Starter",
        "price_pkr": 0,
        "interval": "month",
        "limits": {
            "seats": 1,
            "active_cases": 25,
            "storage_mb": 500,
            "ai_messages_month": 100,
        },
        "features": {"cases", "clients", "documents", "ai_assistant", "tax", "finance"},
    },
    "chamber": {
        "code": "chamber",
        "name": "Chamber",
        "price_pkr": 7500,
        "interval": "month",
        "limits": {
            "seats": 5,
            "active_cases": UNLIMITED,
            "storage_mb": 10_240,
            "ai_messages_month": 2_000,
        },
        "features": {
            "cases", "clients", "documents", "ai_assistant", "tax", "finance",
            "legal_research", "ocr", "mfa", "roles", "audit_log", "intake",
        },
    },
    "firm": {
        "code": "firm",
        "name": "Firm",
        "price_pkr": UNLIMITED,  # custom / contact sales
        "interval": "month",
        "limits": {
            "seats": UNLIMITED,
            "active_cases": UNLIMITED,
            "storage_mb": UNLIMITED,
            "ai_messages_month": UNLIMITED,
        },
        "features": {
            "cases", "clients", "documents", "ai_assistant", "tax", "finance",
            "legal_research", "ocr", "mfa", "roles", "audit_log", "intake",
            "sso", "api", "priority_support",
        },
    },
}

DEFAULT_PLAN = "free"
TRIAL_PLAN = "chamber"  # trials get Chamber-tier features
TRIAL_DAYS = 14
GRACE_DAYS = 2  # read-only grace after a payment becomes past due


def get_plan(code: str | None) -> dict[str, Any]:
    return PLANS.get(code or DEFAULT_PLAN, PLANS[DEFAULT_PLAN])


def plan_limit(code: str | None, key: str) -> int:
    return get_plan(code)["limits"].get(key, UNLIMITED)


def plan_has_feature(code: str | None, feature: str) -> bool:
    return feature in get_plan(code)["features"]
