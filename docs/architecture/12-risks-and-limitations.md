# 12 — Technical Risks, Legal-Data Limitations & Security Concerns

An honest register. These are the things most likely to hurt the project; each has an owner-level mitigation.

## A. Legal-data availability & accuracy (highest risk)

| Risk | Reality | Mitigation |
|------|---------|-----------|
| Official sites block or disallow automated access | Several Pakistani legal portals have no API, may disallow scraping, or change layout | Respect robots/ToS; per-source defensive clients; **degrade to manual-link + `pending`**, never fake |
| Fabricated/outdated citations | LLMs hallucinate citations confidently; stale law is dangerous | Non-fabrication guarantee: citations only from verified retrieval; schema-reject ungrounded citations; freshness re-verification ([09](09-legal-research-verification.md)) |
| Amendment/repeal/overrule not detected | Automated detection is imperfect | Check where determinable; **explicitly state when not determinable**; lawyer verifies primary source |
| Urdu + scanned documents | OCR accuracy drops on Urdu/low-quality scans | Tesseract + Urdu models + optional cloud OCR; confidence thresholds; human review of low-confidence extractions |
| Source disagreement | Databases can conflict | Mark `conflicting`, show both, never silently pick one |

> Bottom line: the platform is a **force multiplier for lawyers, not a substitute for primary-source verification.** This is stated in-product, not buried.

## B. AI correctness & safety

| Risk | Mitigation |
|------|-----------|
| Prompt injection via documents/web | Channel separation, sandboxed data blocks, no tool-calls from untrusted content, CI injection evals ([08](08-ai-agent-architecture.md)) |
| Over-reliance on AI conclusions | Human-approval gates on conclusions/drafts/comms; outputs marked DRAFT; alternatives shown; never declares guilt/innocence |
| Confidential data leaking to LLM providers | `ai_gateway` enforces per-org provider/privacy policy; self-hosted option; nothing leaves without authorization |
| Cost blow-ups | Per-org token/cost accounting + rate limits + caching |

## C. Security & privacy

| Risk | Mitigation |
|------|-----------|
| Cross-tenant data leakage | `organization_id` everywhere + RLS backstop + dedicated isolation test suite |
| Broken authorization | Backend-enforced RBAC + resource-scope checks + audit of denials; frontend guards are UX only |
| Document/credential exposure | Private storage, presigned URLs, field encryption, Argon2id, secrets manager, malware scanning |
| "Secure" claimed too early | Security is verified only in Phase 6 (ASVS + pen test) before real data; pre-prod until then |

## D. Delivery & scope

| Risk | Mitigation |
|------|-----------|
| Scope is very large for a small team | Phased roadmap; test-before-advance; **recommended MVP: one case type + one province first** |
| "Demo works" mistaken for "production ready" | Explicit exit criteria per phase; no fake data; `PROGRESS.md` tracks real status |
| Solo bus-factor / burnout | Realistic 6–9 month estimate; modular design enables adding contributors later |

## E. Legal & ethical (non-code, but real)

| Concern | Stance |
|---------|--------|
| Unauthorized practice of law / liability | Product assists qualified lawyers; does not give legal advice to end clients; disclaimers + human approval |
| Data protection obligations | Encryption, access control, retention/deletion policies, audit; align with applicable privacy obligations |
| Confidentiality / privilege | Strict access control, tenant isolation, no unauthorized external data sharing; client portal field allowlist |
| Court-date reliability | Manually entered dates marked `unconfirmed`; no claim of official confirmation without an official source |

## Recommended first cut (to de-risk)
Build the **chamber management core (Phases 1–2)** + **one AI vertical** (case-specific chatbot over authorized documents, Phase 3) to a real, tested standard before attempting the full legal-web-verification engine (Phase 4). That sequence delivers daily value early and isolates the hardest risk until the foundation is solid.
