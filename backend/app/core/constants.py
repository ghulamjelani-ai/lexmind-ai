"""Domain constants for case management.

Categories are an open set: callers pick a known category, or "other" plus a
free-text custom_category. Statuses and priorities are closed sets.
"""

from __future__ import annotations

# Case categories (prompt §4). "other" allows a custom_category label.
CASE_CATEGORIES: list[str] = [
    "criminal",
    "murder",
    "attempted_murder",
    "theft",
    "robbery",
    "fraud",
    "cybercrime",
    "civil",
    "property",
    "family",
    "divorce",
    "inheritance",
    "constitutional",
    "corporate",
    "banking",
    "bail",
    "other",
]

CASE_STATUSES: list[str] = [
    "open",
    "under_investigation",
    "in_hearing",
    "pending",
    "on_hold",
    "closed",
    "archived",
]
DEFAULT_CASE_STATUS = "open"

CASE_PRIORITIES: list[str] = ["critical", "high", "medium", "low"]
DEFAULT_CASE_PRIORITY = "medium"

# Role a user plays on a specific case.
CASE_ROLES: list[str] = ["primary", "supporting"]

# Party types on a case.
PARTY_TYPES: list[str] = ["client", "opposite", "witness", "other"]

# Timeline event types (append-only case_events).
EVENT_CASE_CREATED = "case_created"
EVENT_CASE_UPDATED = "case_updated"
EVENT_LAWYER_ASSIGNED = "lawyer_assigned"
EVENT_STATUS_CHANGED = "status_changed"
EVENT_PRIORITY_CHANGED = "priority_changed"
EVENT_NOTE_ADDED = "note_added"
EVENT_PARTY_ADDED = "party_added"
