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
EVENT_HEARING_SCHEDULED = "hearing_scheduled"
EVENT_DOCUMENT_UPLOADED = "document_uploaded"

# Hearings. A manually-entered hearing is "unconfirmed" until matched against an
# official source (honesty rule, prompt §9).
HEARING_STATUSES: list[str] = ["unconfirmed", "confirmed", "held", "adjourned", "cancelled"]
DEFAULT_HEARING_STATUS = "unconfirmed"

# Tasks.
TASK_STATUSES: list[str] = ["open", "in_progress", "blocked", "done", "cancelled"]
DEFAULT_TASK_STATUS = "open"

# Approvals.
APPROVAL_TARGETS: list[str] = ["document", "research_report", "case_analysis", "case"]
APPROVAL_STATUSES: list[str] = ["pending", "approved", "rejected"]

# Notifications.
NOTIFICATION_CHANNELS: list[str] = ["in_app", "email"]

# Documents.
DOCUMENT_CATEGORIES: list[str] = [
    "fir",
    "police_report",
    "witness_statement",
    "court_order",
    "charge_sheet",
    "medical_report",
    "agreement",
    "contract",
    "evidence",
    "judgment",
    "correspondence",
    "other",
]
DOC_SCAN_PENDING = "pending"
DOC_SCAN_CLEAN = "clean"
DOC_SCAN_INFECTED = "infected"
