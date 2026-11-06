# LexMind AI — Progress Checklist

Single source of truth for status. A box is checked only when the feature is **implemented and tested**, not when it merely renders.

## Phase 0 — Project setup
- [ ] Repo layout + Docker Compose (api, web, db+pgvector, redis, worker, minio, mailhog)
- [ ] Backend scaffold with `uv`; Next.js scaffold; lint/format; CI skeleton; `.env.example`
- [ ] `docker compose up` brings the full stack up

## Phase 1 — Foundation
- [ ] Identity/tenancy schema + Alembic migrations + RLS policies
- [ ] Auth: Argon2id, sessions, MFA, secure password reset
- [ ] RBAC engine + permission catalog + resource-scope checks
- [ ] Organizations, users, roles, invites
- [ ] Dashboard shell with role-filtered navigation
- [ ] Tests: auth, authorization, cross-tenant isolation

## Phase 2 — Law Chamber Management
- [ ] Case management (full profile, categories+custom, timeline, search/filter/sort/pagination)
- [ ] Clients + conflict-of-interest; assignments/transfers
- [ ] Documents (upload, validation, malware scan, storage, versioning, permissions, preview)
- [ ] Tasks + approvals
- [ ] Hearings + calendar (unconfirmed-date honesty rule)
- [ ] Notifications (in-app + email)
- [ ] Tests: CRUD, per-module authz, upload security, assignment scoping

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
