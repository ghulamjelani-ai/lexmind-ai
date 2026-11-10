"""Automated citation cross-check.

A provision is only ever marked "verified" when the cited section is actually
found in content retrieved from an OFFICIAL source. Absence is reported as
"unverified" (we looked and could not confirm), never as verified; an official
source that shows the section as omitted/repealed/substituted is flagged
"conflicting" for a human to resolve. Nothing here invents a citation — it only
corroborates one the caller already holds (docs/architecture/09).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.rbac import AuthContext
from app.integrations.legal_search import search_official
from app.models.legal import LegalProvision
from app.services import audit_service

# Words that, next to the cited section in official text, mean the section is no
# longer in force as cited — a human must reconcile the citation.
_AMENDMENT_HINTS = re.compile(
    r"\b(omitted|repealed|substituted|deleted|amended|superseded)\b", re.IGNORECASE
)


@dataclass
class CitationVerdict:
    status: str  # verified | conflicting | unverified | pending
    matched_url: str | None = None
    note: str = ""


def _section_pattern(section: str) -> re.Pattern[str] | None:
    """Build a matcher for a section reference such as "302", "302-A", "9(c)".

    Matches the number optionally preceded by section/sec/s./§ and tolerant of
    the letter/clause suffix, as a whole token so "302" does not match "3029"."""
    s = section.strip()
    if not s:
        return None
    m = re.match(r"\s*(?:section|sec\.?|s\.?|§)?\s*(\d+)\s*[-\s]?([A-Za-z])?", s, re.IGNORECASE)
    if not m:
        return None
    num = m.group(1)
    suffix = m.group(2)
    core = re.escape(num)
    if suffix:
        core += rf"[-\s]?{re.escape(suffix)}"
    return re.compile(rf"(?:section|sec\.?|s\.?|§)\s*{core}\b|(?<![\d]){core}\b", re.IGNORECASE)


def check_text(section: str, text: str) -> tuple[bool, bool]:
    """Return (found, amendment_hint) for the section within a block of text."""
    pattern = _section_pattern(section)
    if pattern is None or not text:
        return (False, False)
    match = pattern.search(text)
    if not match:
        return (False, False)
    # Look for an amendment word in a window around the match.
    start = max(0, match.start() - 120)
    window = text[start : match.end() + 120]
    return (True, bool(_AMENDMENT_HINTS.search(window)))


def classify(section: str, official_blocks: list[tuple[str, str]]) -> CitationVerdict:
    """Decide a verdict from (url, content) pairs retrieved from official sources."""
    if not official_blocks:
        return CitationVerdict(
            status="pending",
            note="No official-source result to check against; citation remains unverified.",
        )
    conflict_url: str | None = None
    for url, content in official_blocks:
        found, amended = check_text(section, content)
        if found and amended:
            conflict_url = conflict_url or url
        elif found:
            return CitationVerdict(
                status="verified", matched_url=url, note="Section found in official-source content."
            )
    if conflict_url:
        return CitationVerdict(
            status="conflicting",
            matched_url=conflict_url,
            note="Official source references this section as amended/omitted — confirm manually.",
        )
    return CitationVerdict(
        status="unverified",
        note="Searched official sources but the cited section was not found; verify manually.",
    )


def verify_provision(
    db: Session,
    ctx: AuthContext,
    provision: LegalProvision,
    *,
    search_fn=search_official,
) -> CitationVerdict:
    section = provision.section or ""
    query = f"{provision.law_name} section {section}".strip()
    results = search_fn(query) if section else []
    verdict = classify(section, [(r.url, r.content) for r in results])

    provision.verification_status = verdict.status
    if verdict.matched_url:
        provision.source_url = verdict.matched_url
    provision.retrieved_at = datetime.now(tz=UTC)

    audit_service.record(
        db,
        action="legal.citation_check",
        result="allow",
        organization_id=ctx.organization_id,
        actor_id=ctx.user_id,
        resource_type="legal_provision",
        resource_id=str(provision.id),
        metadata={"status": verdict.status, "results": len(results)},
    )
    return verdict
