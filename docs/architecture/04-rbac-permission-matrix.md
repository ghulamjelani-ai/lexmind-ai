# 04 — User Roles & Permission Matrix

## Model

- **Roles** are per-organization. A user has one or more roles within an org.
- **Permissions** are `action` on a `resource_type`, optionally narrowed by **scope**:
  - `all` — any resource in the org (admin-level).
  - `assigned` — only resources the user is assigned to.
  - `own` — only resources the user created / owns.
  - `self` — the user's own account/profile.
- **Resource-level checks** always run at the backend: even with `cases:read:assigned`, the service verifies the specific case is in the user's assignment set.
- The **Chamber Owner can customize** role→permission bindings; the matrix below is the secure default.

Legend: ✅ full · 🟡 scoped (assigned/own) · 👁 read-only · ➖ none · ⚠ requires approval

## Role × capability matrix

| Capability | Owner/Super Admin | Senior Advocate | Junior/Associate | Legal Researcher | Clerk/Staff | Client |
|---|---|---|---|---|---|---|
| Manage org / billing / subscription | ✅ | ➖ | ➖ | ➖ | ➖ | ➖ |
| Create/manage user accounts & invites | ✅ | ➖ | ➖ | ➖ | ➖ | ➖ |
| Assign roles & permissions | ✅ | ➖ | ➖ | ➖ | ➖ | ➖ |
| Configure AI / system settings | ✅ | ➖ | ➖ | ➖ | ➖ | ➖ |
| View activity / audit logs | ✅ | 👁 (team) | ➖ | ➖ | ➖ | ➖ |
| View all chamber cases | ✅ | 👁 | ➖ | ➖ | ➖ | ➖ |
| View assigned cases | ✅ | 🟡 | 🟡 | 🟡 (for research) | 🟡 (admin fields) | 🟡 (own cases) |
| Create case | ✅ | ✅ | ✅ | ➖ | ➖ | ➖ |
| Edit case core fields | ✅ | 🟡 | 🟡 | ➖ | 🟡 (admin fields only) | ➖ |
| Assign / transfer cases | ✅ | 🟡 (team) | ➖ | ➖ | ➖ | ➖ |
| Add case updates / notes | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | ➖ |
| Upload documents | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 (requested only) |
| Download documents | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 (authorized only) |
| Manage clients | ✅ | 🟡 | 👁 | ➖ | 🟡 (admin) | ➖ |
| Manage hearings / calendar | ✅ | 🟡 | 🟡 | ➖ | ✅ (schedule) | 👁 (own) |
| Create / assign tasks | ✅ | 🟡 | 🟡 (own) | 🟡 (own) | 🟡 | ➖ |
| Request AI case analysis | ✅ | 🟡 | 🟡 | 🟡 | ➖ | ➖ |
| Run legal research agent | ✅ | ✅ | ✅ | ✅ | ➖ | ➖ |
| Generate draft documents | ✅ | 🟡 | 🟡 | 🟡 | ➖ | ➖ |
| **Approve** documents / reports | ✅ | ✅ | ➖ (submit only ⚠) | ➖ (submit only ⚠) | ➖ | ➖ |
| Override case priority | ✅ | 🟡 | ➖ | ➖ | ➖ | ➖ |
| View chamber-wide analytics | ✅ | 👁 (team) | 👁 (own) | 👁 (own) | ➖ | ➖ |
| Communicate with client (external) | ✅ | ✅ ⚠ | 🟡 ⚠ | ➖ | 🟡 ⚠ | ✅ (own lawyers) |
| View own cases (client portal) | — | — | — | — | — | ✅ |

## Permission catalog (sample, not exhaustive)

```
cases:create            cases:read:{all|assigned|own}     cases:update:{all|assigned}
cases:assign            cases:transfer                    cases:delete (soft)
documents:upload        documents:read:{all|assigned}     documents:download:{authorized}
documents:approve       clients:manage:{all|assigned}     hearings:manage:{all|assigned}
tasks:create            tasks:update:{assigned|own}       ai:analysis:request
ai:research:run         ai:draft:generate                 approvals:grant
priority:override       analytics:view:{all|team|own}     admin:users:manage
admin:roles:manage      admin:ai:configure                audit:read:{all|team}
```

## Enforcement layers (defense in depth)

1. **Frontend:** hides unauthorized nav/actions (UX only — never trusted).
2. **API dependency:** FastAPI dependency resolves the caller, their org, roles, permissions; rejects unauthorized `action:resource` early.
3. **Service layer:** `can(user, action, resource_instance)` re-checks scope against the *actual* row (assignment set, ownership).
4. **Database (RLS):** PostgreSQL row-level security policies filter by `organization_id` as a last-resort backstop.
5. **Audit:** every sensitive action and every denied attempt is logged.

## Client portal isolation
Clients are a distinct principal type. They can **only** see their own cases, approved updates, authorized documents, and their assigned lawyers — never internal notes, AI analysis drafts, other clients, or unapproved content. Client-visible fields are an explicit allowlist, not a denylist.
