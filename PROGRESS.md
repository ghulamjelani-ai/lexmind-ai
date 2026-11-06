# LexMind AI — Progress Checklist

Single source of truth for status. A box is checked only when the feature is **implemented and tested**, not when it merely renders.

## Phase 0 — Project setup
- [x] Repo layout + Docker Compose (api, web, db+pgvector, redis, worker, minio, mailpit)
- [x] Backend scaffold with `uv` (FastAPI, health, tests); Next.js scaffold (TS+Tailwind); ruff + eslint; CI skeleton; `.env.example`
- [~] `docker compose up` brings the full stack up (compose config validated with `docker compose config`; full `up --build` not yet run — Docker Desktop daemon was not running in the setup session. Start Docker Desktop, then run `docker compose up --build` to confirm.)

## Phase 1 — Foundation
- [x] Identity/tenancy schema + Alembic migrations (org, user, role, permission, bindings, session, invite, password-reset, audit) — validated on real Postgres (native uuid)
- [x] RLS policies (Postgres backstop) — restricted `lexmind_app` role + RLS on all 9 tenant tables, scoped by the `app.current_org` GUC; two-connection design (privileged auth bootstrap + restricted tenant session). Verified live: fail-closed with no tenant set, strict per-org visibility, cross-org inserts blocked by WITH CHECK; end-to-end over HTTP too. Skip-guarded PG integration test in tests/integration/
- [x] Auth — Argon2id hashing + server-side sessions (hashed tokens, httpOnly cookie); MFA (TOTP) enroll/activate/disable + login enforcement; secure single-use password reset (invalidates sessions)
- [x] RBAC engine + permission catalog + role→permission scopes (endpoint-level gating done; resource-level `scope_for` ready for when case/doc modules land)
- [x] Organizations, users, roles, invites — provisioning, user CRUD (create/list), role listing, invite create + accept flow
- [x] Dashboard shell with role-filtered navigation — Next.js login (cookie auth), client auth context with `can()`, role-filtered sidebar, dashboard home, real Users page (list + create), section stubs. Verified live in-browser against the running backend (owner sees full nav + 6 users; junior sees reduced nav)
- [x] Tests: auth, authorization, cross-tenant isolation + MFA, password reset, invites (25 passing, SQLite in-memory); + Postgres RLS integration suite

## Phase 2 — Law Chamber Management
- [x] Case management — full profile (categories+custom, court/FIR/district fields), status/priority, append-only timeline, assignments (primary/supporting), parties, notes, search/filter/sort/pagination. Scope-aware access (RBAC assigned/own/all enforced per case). RLS on all new tenant tables. Verified on Postgres end-to-end
- [x] Clients + conflict-of-interest — CRUD (CNIC encrypted at rest), name/opposing-party conflict check
- [ ] Documents (upload, validation, malware scan, storage, versioning, permissions, preview)
- [ ] Tasks + approvals
- [ ] Hearings + calendar (unconfirmed-date honesty rule)
- [ ] Notifications (in-app + email)
- [~] Tests: cases + clients covered (CRUD, per-module authz, scope/assignment, tenant isolation, conflict, timeline — 36 SQLite + 4 PG). Upload security pending with documents module

## Phase 3 — AI Foundation
- [ ] `ai_gateway` + configurable LLM provider + embeddings
- [ ] RAG ingestion pipeline (extract → OCR → chunk → embed → pgvector + access metadata)
- [ ] Hybrid retrieval with per-request authorization filtering
- [ ] AI chatbot (general + case mode), streaming, conversations, citations, feedback
- [ ] Prompt-injection sandbox + eval suite
- [ ] Tests: retrieval authorization, injection evals, streaming

## Phase 4 — Legal Intelligence
- [ ] Official legal web-source clients + verification pipeline
- [ ] Legislation verification + judgment retrieval
- [ ] Legal research agent (mandatory citation format)
- [ ] Case analysis (18-section report) + evidence analysis + approval gates
- [ ] Tests: citation verification accuracy, hallucination evals, non-fabrication guarantees

## Phase 5 — Intelligent Automation
- [ ] Explainable case prioritization + audited override
- [ ] Hearing reminders (configurable intervals)
- [ ] Workload analytics + dashboards + reports (CSV/PDF, permission-gated)
- [ ] AI document generation (draft-until-approved) + approval workflows
- [ ] Tests: priority explainability, override audit, reminder scheduling, report permissions

## Phase 6 — Security & Production
- [ ] OWASP ASVS walkthrough
- [ ] SAST/DAST + dependency scanning in CI
- [ ] Penetration-test-style review (authz, isolation, upload, injection, session)
- [ ] Performance/load optimization
- [ ] Centralized logging/monitoring/alerting
- [ ] Backups + restore drills; data retention/deletion jobs
- [ ] Deployment (managed services + secrets manager) + runbooks
- [ ] **Gate:** verification passing → fit to onboard real client data

---
_Last updated: 2026-11-07 — architecture complete, implementation not started._
