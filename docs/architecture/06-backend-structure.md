# 06 — Backend Folder Structure

Modular monolith: one FastAPI app, clean module boundaries, a shared core, and Celery workers in the same codebase. Dependencies flow **inward** (api → services → models/core); the AI subsystem is reachable only via `ai_gateway`.

```
backend/
├── pyproject.toml              # deps managed with uv (NOT pip)
├── uv.lock
├── alembic.ini
├── Dockerfile
├── .env.example                # documents required env vars; no real secrets
├── app/
│   ├── main.py                 # FastAPI app factory, router registration, middleware
│   ├── core/
│   │   ├── config.py           # Pydantic Settings, env-driven
│   │   ├── security.py         # Argon2id hashing, token/session helpers
│   │   ├── rbac.py             # permission catalog, can(), FastAPI deps
│   │   ├── tenancy.py          # org context, RLS session setup
│   │   ├── logging.py          # structured logging, correlation IDs
│   │   ├── rate_limit.py       # Redis-backed limiter
│   │   └── errors.py           # typed exceptions -> HTTP responses
│   ├── db/
│   │   ├── base.py             # SQLAlchemy Base, mixins (TimestampMixin, TenantMixin, SoftDeleteMixin)
│   │   ├── session.py          # engine, session factory, tenant-scoped session
│   │   └── migrations/         # Alembic versions
│   ├── models/                 # SQLAlchemy models (one file per aggregate)
│   │   ├── organization.py  user.py  role.py  client.py
│   │   ├── case.py  hearing.py  document.py  task.py
│   │   ├── knowledge.py  citation.py  ai.py  approval.py
│   │   ├── notification.py  calendar.py  audit.py
│   ├── schemas/                # Pydantic request/response models (mirror models/)
│   ├── api/
│   │   ├── deps.py             # shared dependencies (current_user, require(perm))
│   │   └── v1/
│   │       ├── router.py       # aggregates all v1 routers
│   │       ├── auth.py  users.py  orgs.py
│   │       ├── cases.py  clients.py  hearings.py  calendar.py
│   │       ├── documents.py  tasks.py  approvals.py
│   │       ├── notifications.py  analytics.py  reports.py
│   │       ├── ai_assistant.py # chatbot (SSE streaming), conversations
│   │       ├── research.py     # legal research agent endpoints
│   │       ├── analysis.py     # case/evidence analysis endpoints
│   │       └── knowledge.py    # KB ingestion + search
│   ├── services/               # business logic (no HTTP here)
│   │   ├── auth_service.py  rbac_service.py  case_service.py
│   │   ├── client_service.py  document_service.py  hearing_service.py
│   │   ├── task_service.py  approval_service.py  notification_service.py
│   │   ├── priority_service.py        # explainable scoring
│   │   ├── conflict_service.py        # conflict-of-interest checks
│   │   └── analytics_service.py
│   ├── ai/
│   │   ├── gateway.py          # ai_gateway: provider resolution, authz, injection sandbox, logging
│   │   ├── providers/          # pluggable LLM providers (abstract base + impls)
│   │   ├── embeddings.py       # embedding model abstraction
│   │   ├── retrieval.py        # hybrid retrieval (semantic+keyword+filter+rerank)
│   │   ├── prompts/            # versioned prompt templates (system/instruction channel)
│   │   ├── sandbox.py          # untrusted-content wrapping / injection defense
│   │   ├── graphs/             # LangGraph workflows (one per agent)
│   │   │   ├── case_intake.py  document_understanding.py
│   │   │   ├── legal_research.py  legislation_verify.py  judgment_retrieval.py
│   │   │   ├── case_analysis.py  evidence_analysis.py
│   │   │   ├── prioritization.py  hearing_prep.py
│   │   │   ├── drafting.py  case_summary.py
│   │   └── evals/              # hallucination, citation, injection eval harness
│   ├── integrations/
│   │   ├── storage.py          # S3-compatible client, presigned URLs, encryption
│   │   ├── ocr.py              # Tesseract + optional cloud fallback
│   │   ├── web_sources/        # official legal source clients + verifier
│   │   │   ├── base.py  pakistan_code.py  punjab_laws.py
│   │   │   ├── supreme_court.py  lhc.py  verifier.py
│   │   ├── email.py  whatsapp.py  malware_scan.py
│   ├── workers/
│   │   ├── celery_app.py
│   │   └── tasks/              # ocr_tasks, embedding_tasks, ai_tasks,
│   │                           # verification_tasks, notification_tasks
│   └── utils/                  # pure helpers (dates, pagination, text)
├── tests/
│   ├── unit/        integration/     e2e/
│   ├── security/    # authz, cross-tenant isolation, upload, injection
│   ├── ai/          # eval suites (citation verification, hallucination)
│   ├── fixtures/    # SYNTHETIC cases/clients only
│   └── conftest.py
└── scripts/         # seed_synthetic.py, create_superadmin.py, etc.
```

### Rules
- **No controller touches the DB or AI directly** — always through `services/` and `ai/gateway.py`.
- **Tenant scoping is not optional** — models use `TenantMixin`; sessions set the org context; RLS backs it.
- **Prompts live in `ai/prompts/` and are versioned** — never built from untrusted strings; retrieved content is passed as *data* via `sandbox.py`.
- **Workers import services**, not the other way around.
