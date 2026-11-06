# 03 — Module Breakdown

Each module is a cohesive slice with its own API routes, service layer, models, and tests. Modules communicate through service interfaces, not by reaching into each other's tables.

## Core platform modules

### M1 — Identity & Access (auth, RBAC, tenancy)
- Registration (invite-based), login, logout, session management, MFA.
- Password hashing (Argon2id), secure reset, session expiration.
- Organizations (tenants), users, roles, permissions, user-role bindings.
- Resource-level permission checks (`can(user, action, resource)`).
- Audit logging of auth + permission events.
- **Depends on:** nothing. **Everything depends on it.**

### M2 — Case Management (core)
- Case CRUD with full profile (see prompt §4), categories (+ custom), status, priority.
- Case assignments (primary + supporting lawyers), transfers.
- Case parties (client, opposite party, witnesses).
- Case events / chronological timeline (append-only).
- Search, filter, sort, pagination.
- **Depends on:** M1, M4 (clients), M5 (documents).

### M3 — Hearings & Calendar
- Hearings (date, court, status, notes), previous/next hearing tracking.
- Centralized calendar (daily/weekly/monthly).
- Deadlines (submissions, follow-ups), overdue detection, inactivity detection.
- **Honest-state rule:** a manually entered hearing date is `unconfirmed` until matched against an official cause list (where integration exists).
- **Depends on:** M1, M2.

### M4 — Clients & CRM
- Client records, contact, address, case relationships, communication history.
- Onboarding, conflict-of-interest checking (name/party matching across cases).
- Appointment scheduling, document requests.
- **Depends on:** M1.

### M5 — Documents & Storage
- Upload (PDF/DOCX/images), validation, malware scanning, categorization.
- Private object storage, presigned downloads, previews.
- Versioning + revision history, document-level permissions.
- Full-text search (feeds M7 ingestion).
- **Depends on:** M1.

### M6 — Tasks & Approvals
- Task assignment, status, due dates, overdue alerts.
- Approval workflows (documents, research reports, record changes, client comms, high-impact AI actions).
- **Depends on:** M1, M2.

### M7 — Knowledge Base & RAG ingestion
- Ingestion pipeline: validate → extract text → OCR if needed → metadata → chunk → embed → store in pgvector with access-control metadata.
- Hybrid retrieval service (semantic + keyword + metadata filters + re-rank) with per-request authorization filtering.
- **Depends on:** M1, M5. **Serves:** M9, M10.

### M8 — Notifications
- In-app, email, optional WhatsApp (authorized BSP only).
- Configurable reminder intervals (7/3/1/0 days before hearing, etc.).
- Dispatch via Celery.
- **Depends on:** M1; triggered by M3, M6.

## AI / intelligence modules

### M9 — AI Legal Assistant (chatbot + workflows gateway)
- Two modes: general legal research; case-specific assistant (authorized case context only).
- Conversations, messages, streaming, citations, attachments, regenerate, export, feedback.
- Entry point to the agent workflows in M10/M11.
- **Depends on:** M1, M7, `ai_gateway`.

### M10 — Legal Research & Verification
- Legal Research Agent workflow (understand → jurisdiction → domain → search official sources → extract → compare → verify citations → answer with references).
- Legislation verification + judgment retrieval against official sources (see [09](09-legal-research-verification.md)).
- Mandatory citation format + `verification_status` on every reference.
- **Depends on:** M1, M7, web verification service, `ai_gateway`.

### M11 — Case & Evidence Analysis
- Document Understanding, Case Analysis, Evidence Analysis agents.
- Structured case analysis report (18-section format from prompt §5), with alternative interpretations and explicit "requires lawyer verification" items.
- Never declares guilt/innocence or a final offence.
- **Depends on:** M2, M5, M7, M10, `ai_gateway`.

### M12 — Case Prioritization
- Explainable dynamic priority score (Critical/High/Medium/Low) from deadlines, hearing proximity, bail/custody urgency, missing docs, inactivity, workload.
- Human override with audit record. Popularity/wealth/media explicitly excluded as factors.
- **Depends on:** M2, M3, M6.

### M13 — Drafting & Reports
- Legal Drafting Agent (notices, applications, petitions, bail applications, summaries, correspondence, draft arguments) using chamber-approved templates.
- Every generated document is a `draft` until lawyer-approved; versioned.
- **Depends on:** M5, M7, M6 (approvals), `ai_gateway`.

## Analytics & admin modules

### M14 — Dashboards & Analytics
- Chamber dashboard + individual lawyer dashboard (prompt §12).
- Reports (prompt §19) with CSV/PDF export, permission-gated.
- **Depends on:** read-only across M2–M13.

### M15 — Admin & Settings
- Org/subscription/billing, AI configuration, system settings, activity logs view, data retention/deletion policy controls.
- **Depends on:** M1.

## Module dependency summary

```
M1 (Identity) ─ foundation for all
M5 (Docs) ──► M7 (RAG) ──► M9/M10/M11/M13 (AI)
M2 (Cases) ──► M3, M6, M11, M12
M4 (Clients) ──► M2
M14 (Analytics) reads everything; writes nothing
```
