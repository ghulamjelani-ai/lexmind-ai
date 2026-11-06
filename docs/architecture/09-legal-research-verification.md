# 09 — Legal Web Research & Source Verification Architecture

> This is the platform's highest technical and reputational risk. In law, a fabricated or outdated citation is worse than no answer. This architecture is built around a single rule: **never present an unverified legal fact as verified.**

## Official source priority

| Tier | Sources | Trust |
|------|---------|-------|
| **Primary — Federal legislation** | Pakistan Code (pakistancode.gov.pk) | authoritative (with the caveat below) |
| **Primary — Provincial** | Punjab Laws Portal (punjablaws.gov.pk), Punjab Law & Parliamentary Affairs | authoritative |
| **Primary — Judicial** | Supreme Court (supremecourt.gov.pk), Lahore High Court (lhc.gov.pk), Punjab Judicial Academy (pja.gov.pk), other official HC/district portals | authoritative |
| **Secondary** | reputable legal databases | corroborating only |
| **Never authoritative** | blogs, forums, aggregators | may surface leads, never cited as law |

> **Pakistan Code's own caveat:** parts of its material are under review and the original Gazette notification should be consulted in case of doubt. The system treats Pakistan Code text as authoritative-but-reviewable and surfaces this caveat to the user when a provision is relied upon.

## Verification pipeline

```
 query
   │
   ▼
 ┌────────────────────┐
 │ 1. plan search      │  identify jurisdiction, domain, target source tier
 └─────────┬──────────┘
           ▼
 ┌────────────────────┐
 │ 2. retrieve         │  (a) internal verified cache (legal_provision/judgment)
 │                     │  (b) live fetch from official sources IF allowed by robots/ToS
 └─────────┬──────────┘
           ▼
 ┌────────────────────┐
 │ 3. extract passage  │  pull exact section/para text + metadata (date, court)
 └─────────┬──────────┘
           ▼
 ┌────────────────────┐
 │ 4. VERIFY           │  cross-check the citation against the official source:
 │                     │   - does the section/article number exist & match text?
 │                     │   - publication / judgment date present?
 │                     │   - amended / repealed / overruled / distinguished?
 │                     │   - source URL reachable & official?
 └─────────┬──────────┘
           ▼
 ┌────────────────────┐
 │ 5. assign status    │  verified | pending | unverified | conflicting
 │                     │  + retrieved_at timestamp + source_url (preserved)
 └─────────┬──────────┘
           ▼
 ┌────────────────────┐
 │ 6. answer w/ refs   │  mandatory citation format; unverifiable items flagged
 └────────────────────┘
```

## Mandatory citation record (every provision/judgment)

```
law_or_judgment_name
section_or_article
case_citation (if any)
court_name
judgment_or_publication_date (only if verified; else null + note)
paragraph_or_page
short_explanation
source_url                      (original, preserved)
retrieved_at                    (timestamp)
verification_status             verified | pending | unverified | conflicting
treatment                       binding | persuasive | non-binding | (distinguished/overruled if known)
```

## The non-fabrication guarantees

The system **never** generates any of the following from the model's own "knowledge":
citations · judgment numbers · section numbers · court names · legal quotations · dates · URLs.

Each of these must come from a retrieved, verifiable source. If retrieval/verification fails:
- the item is returned with `verification_status = unverified` or `pending`,
- a **manual source link** is provided for the lawyer to check,
- the answer explicitly states the limitation.

An LLM node that cannot ground a claim is instructed to say so — not to fill the gap. Output is schema-validated: a citation object missing a real `source_url` is rejected.

## Access, legality, and honesty about limits

- **Respect robots.txt and Terms of Service.** We do **not** bypass access controls or scrape against a site's terms. Where automated access is unavailable or disallowed, the system provides a **manual source link** and marks verification `pending` — it does not fake a result.
- **Site reliability is a real constraint.** Official Pakistani legal portals vary in availability, structure, and machine-readability; some have no clean API and change layout without notice. The web-source clients (`integrations/web_sources/`) are written per-source, defensively, and degrade to "manual verification required" rather than guessing.
- **Discrepancies are surfaced, not resolved silently.** If official databases disagree, the citation is marked `conflicting` and both sources are shown.
- **Amendment/repeal awareness.** Where determinable, provisions are checked for amending Acts/Gazette notifications and judgments for subsequent treatment; where not determinable, this is stated.

## Caching & freshness
- Verified provisions/judgments are cached (`legal_provision`, `judgment`) with `retrieved_at`; cache entries expire and re-verify on a schedule and before being cited in a new approved report.
- Caching reduces load on official sites and improves reliability, but a cached item past its freshness window is re-verified before reuse in anything a lawyer approves.

## Honest statement of capability
This system **accelerates and organizes** legal research with traceable sources. It does **not** replace a lawyer checking the primary source. Every citation links back to its origin precisely so a qualified lawyer can verify it. Where we cannot verify, we say so — clearly and by default.
