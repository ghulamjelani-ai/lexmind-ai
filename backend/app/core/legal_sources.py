"""Official Pakistani legal sources and verification vocabulary.

Primary (government/judicial) sources are authoritative; everything else is
corroborating at best. The platform prefers these and, where it cannot verify
against them automatically, provides a manual link and marks the item pending —
it never fabricates (see docs/architecture/09).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LegalSource:
    key: str
    name: str
    url: str
    tier: str  # "federal_legislation" | "provincial_legislation" | "judicial"
    jurisdiction: str  # "federal" | "punjab" | ...
    authoritative: bool


OFFICIAL_SOURCES: list[LegalSource] = [
    LegalSource(
        "pakistan_code", "Pakistan Code", "https://pakistancode.gov.pk/",
        "federal_legislation", "federal", True,
    ),
    LegalSource(
        "punjab_laws", "Punjab Laws Portal", "https://punjablaws.gov.pk/",
        "provincial_legislation", "punjab", True,
    ),
    LegalSource(
        "supreme_court", "Supreme Court of Pakistan", "https://www.supremecourt.gov.pk/",
        "judicial", "federal", True,
    ),
    LegalSource(
        "lahore_high_court", "Lahore High Court", "https://lhc.gov.pk/",
        "judicial", "punjab", True,
    ),
    LegalSource(
        "punjab_judicial_academy", "Punjab Judicial Academy", "https://pja.gov.pk/",
        "judicial", "punjab", True,
    ),
]

# Verification status for any cited provision or judgment.
VERIFICATION_STATUSES: list[str] = ["verified", "pending", "unverified", "conflicting"]
DEFAULT_VERIFICATION_STATUS = "pending"

# How a precedent binds, per applicable legal principles.
TREATMENTS: list[str] = ["binding", "persuasive", "non_binding", "distinguished", "overruled"]


def source_by_key(key: str) -> LegalSource | None:
    return next((s for s in OFFICIAL_SOURCES if s.key == key), None)
