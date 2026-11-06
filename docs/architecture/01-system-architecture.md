# 01 — System Architecture

> LexMind AI — AI-Powered Legal Intelligence & Law Chamber Management Platform
> Target: production, multi-tenant SaaS for law chambers in Pakistan.

## 1. Guiding principles

1. **AI assists, lawyers decide.** No legal conclusion is final without a qualified lawyer's review. Every AI output is a *draft* with traceable sources until approved.
2. **Authorization at the backend, always.** Frontend route guards are UX only. Every query is scoped to `organization_id` + resource-level permissions in the service/data layer.
3. **Retrieved content is untrusted data, never instructions.** Documents, web pages, and RAG chunks are sandboxed from the system/instruction channel (prompt-injection defense).
4. **No fabrication of legal facts.** Citations, sections, judgments, dates, and URLs are either verified against official sources or explicitly marked `verification_pending` / `unverified`.
5. **Modular, independently testable.** Each AI capability is a discrete workflow with a defined interface, not one monolithic agent.

## 2. High-level topology

```
                         ┌─────────────────────────────┐
          HTTPS          │        Next.js (App Router)  │
  Browser ──────────────▶│  React + TS + Tailwind + shadcn│
                         │  SSR/CSR, RBAC-aware UI       │
                         └──────────────┬──────────────┘
                                        │ REST (JSON), SSE for streaming
                                        ▼
                         ┌─────────────────────────────┐
                         │        FastAPI (Python)      │
                         │  Auth · RBAC · Services · API │
                         │  Pydantic validation layer    │
                         └───┬───────────┬───────────┬──┘
                             │           │           │
             ┌───────────────┘           │           └────────────────┐
             ▼                           ▼                            ▼
   ┌──────────────────┐      ┌────────────────────┐      ┌────────────────────┐
   │   PostgreSQL     │      │  Redis (broker +    │      │  Object Storage     │
   │  + pgvector      │      │  cache + rate-limit)│      │  (S3-compatible,    │
   │  SQLAlchemy/     │      └─────────┬──────────┘      │  private, presigned) │
   │  Alembic         │                │                 └────────────────────┘
   └──────────────────┘                ▼
                              ┌────────────────────┐
                              │   Celery workers    │
                              │  OCR · embeddings · │
                              │  AI workflows ·     │
                              │  web verification · │
                              │  notifications      │
                              └─────────┬──────────┘
                                        │
                   ┌────────────────────┼─────────────────────┐
                   ▼                    ▼                     ▼
         ┌──────────────┐   ┌────────────────────┐  ┌──────────────────┐
         │ LLM provider │   │ Official legal web  │  │ Email / WhatsApp │
         │ (configurable)│  │ sources (verify)    │  │ (authorized BSP) │
         └──────────────┘   └────────────────────┘  └──────────────────┘
```

## 3. Request paths

**Synchronous (REST):** CRUD on cases, clients, documents, tasks, calendar; auth; RBAC checks; reads of AI results. Latency-sensitive, returns immediately.

**Asynchronous (Celery):** anything slow or external — OCR, text extraction, embedding generation, multi-step AI workflows (case analysis, legal research), web source verification, bulk notifications. The API enqueues a job, returns a `job_id`, and the client polls or subscribes (SSE) for progress/results. This keeps the API responsive and makes AI steps independently retryable and loggable.

**Streaming (SSE):** chatbot token streaming and long-running workflow progress events. We use Server-Sent Events over WebSockets for simplicity and proxy-friendliness; upgrade to WebSockets only if bidirectional needs appear.

## 4. Multi-tenancy model

- **Shared database, shared schema, `organization_id` discriminator** on every tenant-owned row. Chosen over schema-per-tenant for operational simplicity at early scale; revisit schema-per-tenant or row-level security (RLS) if a chamber requires hard data isolation guarantees.
- Enforcement in three layers: (1) a SQLAlchemy session that injects a tenant filter, (2) explicit service-layer checks, (3) **PostgreSQL Row-Level Security policies** as a backstop so a bug in app code cannot leak cross-tenant data.
- Every audit log, document, embedding, and AI conversation carries `organization_id`.

## 5. AI subsystem boundary

The AI subsystem is reached only through an **internal service interface** (`ai_gateway`), never directly from controllers. This gateway:
- resolves the chamber's configured LLM provider + privacy policy (can the chamber send data to an external provider at all?);
- enforces per-request authorization context (which cases/docs the caller may see) *before* retrieval;
- strips/sandboxes untrusted retrieved content;
- records every step, source, prompt, and result for audit and hallucination review.

See [08-ai-agent-architecture.md](08-ai-agent-architecture.md) and [09-legal-research-verification.md](09-legal-research-verification.md).

## 6. Environments

| Env | Purpose | Notes |
|-----|---------|-------|
| local | dev | Docker Compose: api, web, db, redis, worker, minio (S3), mailhog |
| staging | pre-prod verification | mirrors prod; seeded with synthetic data only |
| production | live | managed Postgres, managed Redis, object storage, secrets manager |

No real confidential client data is ever used outside production without explicit authorization and safeguards (synthetic fixtures only).

## 7. Cross-cutting concerns

- **Config:** environment variables + secrets manager. No secrets in code or images. See [10-security-architecture.md](10-security-architecture.md).
- **Logging:** structured JSON logs, centralized; AI workflow steps logged with correlation IDs. No secrets/PII in logs beyond what's necessary, access-controlled.
- **Observability:** request tracing, Celery task metrics, LLM token/cost accounting per org.
- **Testing:** unit, integration, e2e, plus AI-specific evals (hallucination, citation verification, prompt injection). See [11-development-roadmap.md](11-development-roadmap.md) and the testing section of each module.
