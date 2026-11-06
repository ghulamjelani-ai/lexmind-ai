# 11 — Development Roadmap

Phased, test-before-you-advance. No phase is "done" until its features are implemented **and** tested. The timeboxes below are **honest estimates for one experienced full-stack+AI developer working steadily** — they are ranges, not promises, and the legal-verification and security phases are the ones most likely to run long.

## Phase 0 — Project setup (0.5–1 week)
- Repos/monorepo layout, Docker Compose (api, web, db+pgvector, redis, worker, minio, mailhog).
- `uv` backend project, Next.js frontend, linting/formatting, CI skeleton, `.env.example`.
- **Exit:** `docker compose up` brings the whole stack up; CI runs lint + empty test suite.

## Phase 1 — Foundation (2–4 weeks)
- DB schema + Alembic migrations for identity/tenancy core; RLS policies.
- Auth (Argon2id, sessions, MFA scaffold, password reset), RBAC engine, permission catalog.
- Organizations, users, roles, invites; basic dashboard shell with role-filtered nav.
- **Tests:** auth, authorization, **cross-tenant isolation** from the start.
- **Exit:** a user can be invited, log in, and see only what their role permits; isolation tests green.

## Phase 2 — Law Chamber Management (4–6 weeks)
- Case management (full profile, categories+custom, timeline, search/filter/sort/pagination).
- Clients + conflict-of-interest check; case assignments/transfers.
- Documents (upload, validation, malware scan, storage, versioning, permissions, preview).
- Tasks + approvals; hearings + calendar (with `unconfirmed` honesty rule); notifications (in-app + email).
- **Tests:** CRUD, authz per module, upload security, assignment scoping.
- **Exit:** a chamber can run day-to-day case/client/document/hearing/task work end-to-end.

## Phase 3 — AI Foundation (3–5 weeks)
- `ai_gateway`, configurable LLM provider abstraction, embeddings.
- RAG ingestion pipeline (extract → OCR → chunk → embed → pgvector with access metadata).
- Hybrid retrieval with per-request authorization filtering.
- AI chatbot (general + case mode), streaming, conversations, citations, feedback.
- Prompt-injection sandbox + first eval suite.
- **Tests:** retrieval authorization (no cross-case/tenant leakage), injection evals, streaming.
- **Exit:** a lawyer can chat over authorized case context with sourced answers; injection evals pass.

## Phase 4 — Legal Intelligence (5–8 weeks) ⚠ highest risk
- Official legal web-source clients + verification pipeline ([09](09-legal-research-verification.md)).
- Legislation verification, judgment retrieval, legal research agent.
- Case analysis (18-section report) + evidence analysis; approval gates.
- **Tests:** **citation verification accuracy**, hallucination evals, non-fabrication guarantees, source-status correctness.
- **Exit:** research/analysis produce traceable, verification-tagged outputs; no fabricated citations in evals; unverifiable items correctly flagged.

## Phase 5 — Intelligent Automation (3–5 weeks)
- Explainable case prioritization (+ audited override); hearing reminders with configurable intervals.
- Workload analytics + dashboards + reports (CSV/PDF export, permission-gated).
- AI-generated documents (drafting, templates, draft-until-approved) + approval workflows.
- **Tests:** priority explainability + override audit, reminder scheduling, report permissions.
- **Exit:** cases are prioritized with explanations; nothing high-impact happens without approval.

## Phase 6 — Security & Production (3–5 weeks, ongoing after)
- OWASP ASVS walkthrough; SAST/DAST + dependency scanning in CI; pen-test-style review.
- Performance/load optimization; centralized logging/monitoring/alerting; backups + restore drills.
- Deployment (managed Postgres/Redis/storage, secrets manager), runbooks, data retention/deletion jobs.
- **Exit:** verification checklist passing; only then is the platform fit to onboard real client data.

## Realistic total
Roughly **6–9 months of focused solo work** to a genuinely production-grade v1 — and the legal-verification correctness and security verification are the parts that most often extend that. Faster is possible for a *demo*; production for law chambers is not a demo. Scope can be cut by narrowing to one case type and one province first (recommended MVP path).

## Cross-cutting (every phase)
- Tests written **with** features, not after.
- API docs (OpenAPI) kept current; installation/deployment docs maintained.
- `PROGRESS.md` checklist updated as the single source of truth for status.
- No fake dashboard data standing in for real functionality; no hardcoded legal conclusions.
