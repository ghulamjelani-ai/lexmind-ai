# LexMind AI

**AI-Powered Legal Intelligence & Law Chamber Management Platform** — a production-oriented, secure, multi-tenant SaaS for law chambers and firms in Pakistan.

LexMind helps a chamber manage every case, understand complex matters, research applicable law against **official sources**, prepare documents, prioritize workload, and ensure no case, hearing, or client is neglected — while keeping a qualified lawyer firmly in control of every legal conclusion.

> **Design principle:** The AI assists qualified lawyers; it does not replace their professional judgment. Every legal conclusion is traceable to a verified source and reviewed by a lawyer before it is final.

---

## Status

🟡 **Phase: Architecture & Design (complete).** Implementation has not started. See [PROGRESS.md](PROGRESS.md).

This repository currently contains the architecture deliverables. Code begins at Phase 0/1 per the roadmap.

## Architecture documents

Start here, in order:

1. [System Architecture](docs/architecture/01-system-architecture.md)
2. [Tech Stack Justification](docs/architecture/02-tech-stack-justification.md)
3. [Module Breakdown](docs/architecture/03-module-breakdown.md)
4. [RBAC & Permission Matrix](docs/architecture/04-rbac-permission-matrix.md)
5. [Database ER Diagram](docs/architecture/05-database-er-diagram.md)
6. [Backend Folder Structure](docs/architecture/06-backend-structure.md)
7. [Frontend Folder Structure](docs/architecture/07-frontend-structure.md)
8. [AI Agent Architecture](docs/architecture/08-ai-agent-architecture.md)
9. [Legal Web Research & Source Verification](docs/architecture/09-legal-research-verification.md)
10. [Security Architecture](docs/architecture/10-security-architecture.md)
11. [Development Roadmap](docs/architecture/11-development-roadmap.md)
12. [Risks & Limitations](docs/architecture/12-risks-and-limitations.md)

## Stack (summary)

- **Frontend:** Next.js (App Router), React, TypeScript, Tailwind, shadcn/ui
- **Backend:** Python, FastAPI, Pydantic, SQLAlchemy, Alembic — deps via **`uv`** (not pip)
- **Data:** PostgreSQL + pgvector; Redis; S3-compatible object storage
- **AI:** configurable LLM provider, RAG over pgvector, LangGraph workflows, OCR
- **Async/Infra:** Celery + Redis, Docker + Docker Compose

## Non-negotiables

- Backend-enforced RBAC + multi-tenant isolation (never trust the frontend).
- No fabricated legal citations, sections, dates, or URLs — verified or marked unverified.
- Retrieved content is untrusted data, never instructions (prompt-injection defense).
- Secrets only via environment/secrets manager — never in code.
- No feature is "complete" until implemented **and** tested.

## Getting started (once Phase 0 lands)

Implementation setup (Docker Compose, `uv`, Next.js) will be documented here when Phase 0 is built. Not available yet.

## License

TBD.
