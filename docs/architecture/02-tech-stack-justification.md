# 02 — Technical Stack Justification

Each choice is justified against the real constraints of this platform: confidential legal data, AI correctness, multi-tenant SaaS, and a small (initially solo) team shipping to production.

## Frontend

| Choice | Why | Trade-off accepted |
|--------|-----|--------------------|
| **Next.js (App Router)** | SSR for fast first paint + SEO on public/marketing pages; server components reduce client bundle; mature auth/session patterns. | App Router learning curve; some libraries lag on RSC support. |
| **React + TypeScript** | Type safety across a large domain model (cases, roles, permissions) catches whole classes of bugs before runtime. | More upfront typing effort. |
| **Tailwind CSS + shadcn/ui** | Fast, consistent, accessible components; shadcn is copy-in (no runtime lock-in), easy to theme navy/neutral legal look; dark/light out of the box. | Verbose class strings; team discipline needed. |
| **TanStack Query** | Server-state caching, background refetch, optimistic updates — fits a REST backend well. | — |

## Backend

| Choice | Why | Trade-off accepted |
|--------|-----|--------------------|
| **Python + FastAPI** | Python is the center of gravity for AI/ML (LangGraph, embeddings, OCR, LLM SDKs). FastAPI gives async I/O, automatic OpenAPI docs, and Pydantic validation in one package. | Python concurrency limits for CPU-bound work → offloaded to Celery workers. |
| **Pydantic v2** | Single source of truth for request/response schemas + validation; fast (Rust core). | — |
| **SQLAlchemy 2.0 + Alembic** | Mature ORM with full control over queries (needed for tenant scoping + complex joins); Alembic for versioned migrations. | More boilerplate than a lighter ORM. |
| **uv** (package/deps manager) | Fast, reproducible, lockfile-based Python dependency management; replaces pip/venv juggling. **Project standard — do not use plain pip.** | Newer tool; team must learn it. |

## Database & search

| Choice | Why |
|--------|-----|
| **PostgreSQL** | ACID, mature, excellent for relational legal data with strong constraints; supports RLS for tenant isolation. |
| **pgvector** | Keeps vector search *inside* Postgres — one datastore to secure, back up, and tenant-scope. Avoids a separate vector DB (less surface area, simpler ops, tenant metadata filtering is native SQL). Revisit a dedicated vector DB only if scale demands it. |
| **Hybrid retrieval** | pgvector (semantic) + Postgres full-text (keyword) + metadata filters + re-ranking. Legal search needs exact section/citation matching *and* semantic similarity. |

## AI infrastructure

| Choice | Why |
|--------|-----|
| **Configurable LLM provider** | Chambers have different privacy/cost postures; some may require a self-hosted/regional model for confidentiality. Provider is abstracted behind `ai_gateway`. No provider lock-in. |
| **LangGraph** | Legal workflows are multi-step with branching, retries, and human-approval gates. LangGraph gives explicit, inspectable state machines (vs. opaque agent loops) — essential for auditability and for *not* letting an agent "decide guilt." |
| **RAG over pgvector** | Grounds answers in the chamber's documents + verified legislation, reducing hallucination and enabling source citation. |
| **OCR (Tesseract + optional cloud OCR)** | Pakistani legal docs are often scanned PDFs/images in English and Urdu. Start with Tesseract; allow a cloud OCR fallback for accuracy where the chamber authorizes it. |

## Async & infrastructure

| Choice | Why |
|--------|-----|
| **Celery + Redis** | Battle-tested task queue; Redis doubles as cache + rate-limit store + Celery broker. Keeps the API non-blocking for OCR/AI/web jobs. |
| **Docker + Docker Compose** | Reproducible local + staging; one command to bring up the whole stack. |
| **S3-compatible object storage (MinIO local / managed prod)** | Documents never live on app disk; private buckets + presigned, expiring URLs; server-side encryption. |

## What we deliberately avoid at this stage
- **Microservices** — premature; a well-structured modular monolith (API) + worker is easier to ship and secure solo. Service boundaries are drawn cleanly so extraction is possible later.
- **A separate vector database** — pgvector covers current needs with less operational and security surface.
- **Client-only auth / JWT-in-localStorage** — httpOnly secure cookies + server-side session validation; see security doc.
