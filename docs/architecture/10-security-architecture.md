# 10 — Security Architecture

> This platform holds privileged, confidential legal and personal data. Security is a core architectural requirement, aligned to **OWASP ASVS**. Below is the design, not a claim of completion — items are verified during Phase 6 (audit + pen test) before any real client data is onboarded.

## Authentication
- **Password hashing: Argon2id** with tuned memory/time/parallelism parameters.
- **MFA** (TOTP) available and enforceable per-org; recovery codes stored hashed.
- **Sessions:** server-validated, httpOnly + Secure + SameSite cookies; short-lived access with refresh/rotation; absolute + idle expiration; revocation on logout/password change.
- **Secure password reset:** single-use, time-limited, hashed tokens; no account enumeration in responses.
- **Invite-based onboarding** for staff; no open self-registration into a chamber.

## Authorization
- **RBAC + resource-level scope** enforced at the backend on every request (see [04](04-rbac-permission-matrix.md)).
- **Defense in depth:** API dependency → service-layer `can(user, action, instance)` → **PostgreSQL RLS** per `organization_id`.
- **No reliance on frontend route protection** — ever.
- Every denied attempt is audit-logged.

## Multi-tenant isolation
- `organization_id` on every tenant row; RLS policies as a backstop; cross-tenant isolation is an explicit **test suite** (a lawyer in org A must never read org B's data via any endpoint, search, RAG query, or AI workflow).

## Data protection
- **Encryption in transit:** HTTPS/TLS everywhere; HSTS.
- **Encryption at rest:** database + object storage; sensitive fields (CNIC, MFA secrets) field-encrypted with keys from the secrets manager.
- **Private object storage:** no public buckets; presigned, short-expiry, scoped download URLs; uploads validated + **malware-scanned** before they're usable.
- **Secrets management:** env vars locally, a secrets manager in prod; **no secrets in code, images, or logs** (prompt rule + §2). `.env.example` documents variables with placeholders only.

## Application hardening
- **Input validation** via Pydantic on every endpoint.
- **SQL injection:** parameterized queries / ORM only; no string-built SQL.
- **XSS:** React escaping + output encoding; strict Content-Security-Policy; sanitize any rendered rich text.
- **CSRF:** SameSite cookies + anti-CSRF tokens on state-changing requests.
- **CORS:** explicit allowlist of trusted origins; credentials gated.
- **Rate limiting** (Redis) on auth, AI, and expensive endpoints; abuse/anomaly alerts.
- **File upload security:** type/size validation, content sniffing, malware scan, stored outside app, never executed, served via presigned URLs.

## AI-specific security
- **Retrieved content is untrusted data, not instructions** — channel separation + sandboxing ([08](08-ai-agent-architecture.md)).
- **No confidential data leaves the chamber** without its configured authorization; `ai_gateway` enforces the provider/privacy policy per org.
- **Prompt-injection test suite** in CI; AI outputs schema-validated and scope-checked.
- **Per-org cost/rate controls** to prevent abuse-driven spend.

## Auditing & monitoring
- **Append-only audit log** of auth events, permission grants/denials, record changes, document access, approvals, AI runs, and admin actions — with actor, org, resource, result, IP, timestamp.
- Centralized structured logs; alerting on anomalies (mass download, repeated authz denials, cross-tenant attempts).

## Resilience & lifecycle
- **Backup & recovery:** automated encrypted DB + object-storage backups; periodic restore tests; documented RPO/RTO.
- **Data retention & deletion:** per-org policy; soft-delete for legal-record integrity; hard deletion only via explicit, audited retention jobs honoring legal obligations.
- **Dependency hygiene:** lockfiles (uv, npm), automated vulnerability scanning, timely patching.

## Verification plan (Phase 6, before real-client onboarding)
- OWASP ASVS checklist walkthrough.
- Automated SAST/DAST + dependency scans in CI.
- Third-party-style penetration test (authz, tenant isolation, upload, injection, session).
- Load/performance testing.

> **Honest note:** security here is *designed in from day one*, but "secure" is only earned after the Phase 6 verification above is completed and passing. Until then, treat the system as pre-production and do not load real confidential client data.
