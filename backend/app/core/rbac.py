"""RBAC engine: permission catalog, system-role definitions, and the
authorization context used to gate requests.

Two levels of check:
  * endpoint level  -> `AuthContext.has(code)` (does the user hold the permission at all?)
  * resource level  -> `AuthContext.scope_for(code)` returns all|assigned|own|self,
                       which services use to verify a specific row.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

# --- Scopes, broadest first --------------------------------------------------
SCOPE_ALL = "all"
SCOPE_ASSIGNED = "assigned"
SCOPE_OWN = "own"
SCOPE_SELF = "self"
_SCOPE_RANK = {SCOPE_ALL: 3, SCOPE_ASSIGNED: 2, SCOPE_OWN: 1, SCOPE_SELF: 0}


def broadest(scopes: set[str]) -> str:
    return max(scopes, key=lambda s: _SCOPE_RANK.get(s, -1))


# --- Permission catalog (global) ---------------------------------------------
# (code, human description)
PERMISSIONS: list[tuple[str, str]] = [
    ("admin:org:manage", "Manage organization, billing, subscription"),
    ("admin:users:manage", "Create/manage user accounts and invites"),
    ("admin:roles:manage", "Assign roles and permissions"),
    ("admin:ai:configure", "Configure AI and system settings"),
    ("audit:read", "View activity / audit logs"),
    ("cases:create", "Create cases"),
    ("cases:read", "View cases"),
    ("cases:update", "Edit case fields"),
    ("cases:assign", "Assign / transfer cases"),
    ("cases:delete", "Soft-delete cases"),
    ("documents:upload", "Upload documents"),
    ("documents:read", "View documents"),
    ("documents:download", "Download documents"),
    ("documents:approve", "Approve documents / reports"),
    ("clients:manage", "Manage clients"),
    ("hearings:manage", "Manage hearings and calendar"),
    ("tasks:create", "Create / assign tasks"),
    ("tasks:update", "Update tasks"),
    ("ai:analysis:request", "Request AI case analysis"),
    ("ai:research:run", "Run legal research agent"),
    ("ai:draft:generate", "Generate draft documents"),
    ("approvals:grant", "Approve pending items"),
    ("priority:override", "Override case priority"),
    ("analytics:view", "View analytics and reports"),
]
PERMISSION_CODES = {code for code, _ in PERMISSIONS}

# --- System roles -> [(permission_code, scope)] ------------------------------
OWNER = "owner"
SENIOR_ADVOCATE = "senior_advocate"
JUNIOR_ADVOCATE = "junior_advocate"
LEGAL_RESEARCHER = "legal_researcher"
CLERK = "clerk"
CLIENT = "client"

SYSTEM_ROLES: dict[str, list[tuple[str, str]]] = {
    OWNER: [(code, SCOPE_ALL) for code, _ in PERMISSIONS],
    SENIOR_ADVOCATE: [
        ("audit:read", SCOPE_ASSIGNED),
        ("cases:read", SCOPE_ALL),
        ("cases:update", SCOPE_ASSIGNED),
        ("cases:assign", SCOPE_ASSIGNED),
        ("documents:upload", SCOPE_ASSIGNED),
        ("documents:read", SCOPE_ASSIGNED),
        ("documents:download", SCOPE_ASSIGNED),
        ("documents:approve", SCOPE_ALL),
        ("clients:manage", SCOPE_ASSIGNED),
        ("hearings:manage", SCOPE_ASSIGNED),
        ("tasks:create", SCOPE_ASSIGNED),
        ("tasks:update", SCOPE_ASSIGNED),
        ("ai:analysis:request", SCOPE_ASSIGNED),
        ("ai:research:run", SCOPE_ALL),
        ("ai:draft:generate", SCOPE_ASSIGNED),
        ("approvals:grant", SCOPE_ALL),
        ("priority:override", SCOPE_ASSIGNED),
        ("analytics:view", SCOPE_ASSIGNED),
    ],
    JUNIOR_ADVOCATE: [
        ("cases:create", SCOPE_ALL),
        ("cases:read", SCOPE_ASSIGNED),
        ("cases:update", SCOPE_ASSIGNED),
        ("documents:upload", SCOPE_ASSIGNED),
        ("documents:read", SCOPE_ASSIGNED),
        ("documents:download", SCOPE_ASSIGNED),
        ("tasks:create", SCOPE_OWN),
        ("tasks:update", SCOPE_OWN),
        ("ai:analysis:request", SCOPE_ASSIGNED),
        ("ai:research:run", SCOPE_ALL),
        ("ai:draft:generate", SCOPE_ASSIGNED),
        ("analytics:view", SCOPE_OWN),
    ],
    LEGAL_RESEARCHER: [
        ("cases:read", SCOPE_ASSIGNED),
        ("documents:upload", SCOPE_ASSIGNED),
        ("documents:read", SCOPE_ASSIGNED),
        ("tasks:update", SCOPE_OWN),
        ("ai:research:run", SCOPE_ALL),
        ("ai:draft:generate", SCOPE_ASSIGNED),
        ("analytics:view", SCOPE_OWN),
    ],
    CLERK: [
        ("cases:read", SCOPE_ASSIGNED),
        ("documents:upload", SCOPE_ASSIGNED),
        ("documents:read", SCOPE_ASSIGNED),
        ("clients:manage", SCOPE_ALL),
        ("hearings:manage", SCOPE_ALL),
        ("tasks:create", SCOPE_ALL),
    ],
    CLIENT: [
        ("cases:read", SCOPE_OWN),
        ("documents:download", SCOPE_OWN),
        ("documents:upload", SCOPE_OWN),
    ],
}


@dataclass
class AuthContext:
    """The authenticated caller and their effective permissions."""

    user_id: uuid.UUID
    organization_id: uuid.UUID
    is_client: bool = False
    # permission code -> set of granted scopes
    permissions: dict[str, set[str]] = field(default_factory=dict)

    def has(self, code: str) -> bool:
        return code in self.permissions

    def scope_for(self, code: str) -> str | None:
        scopes = self.permissions.get(code)
        return broadest(scopes) if scopes else None
