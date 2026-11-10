"""Conflict-of-interest screening.

Deterministic, explainable, no AI: a prospective matter is checked against the
chamber's existing clients and the adverse parties on existing cases. The output
is a level (clear / review / block) and a list of hits, each with a reason a
lawyer can act on. This is a professional-responsibility safeguard, so it never
guesses — it reports exact name/email/phone matches and lets the lawyer decide.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.rbac import AuthContext
from app.models.case import Case, CaseParty
from app.models.client import Client

# Party roles that are adverse to our client (so acting for that person conflicts).
_ADVERSE_ROLES = {
    "opposite", "opposing", "opponent", "respondent", "defendant", "accused",
    "complainant", "plaintiff", "petitioner", "adverse",
}


@dataclass
class ConflictHit:
    severity: str  # block | review | info
    kind: str
    reason: str
    match: str


@dataclass
class ConflictReport:
    level: str  # clear | review | block
    hits: list[ConflictHit] = field(default_factory=list)

    def as_dicts(self) -> list[dict]:
        return [vars(h) for h in self.hits]


def _norm(value: str | None) -> str:
    if not value:
        return ""
    # Lowercase, collapse whitespace, drop honorifics/punctuation for name matching.
    v = re.sub(r"[^a-z0-9\s@.+]", " ", value.lower())
    v = re.sub(r"\b(mr|mrs|ms|dr|m/s|messrs|syed|mohammad|muhammad|md)\b", " ", v)
    return re.sub(r"\s+", " ", v).strip()


def screen(
    db: Session,
    ctx: AuthContext,
    *,
    full_name: str,
    opposing_party: str | None = None,
    email: str | None = None,
    phone: str | None = None,
) -> ConflictReport:
    name = _norm(full_name)
    opp = _norm(opposing_party)
    mail = _norm(email)
    ph = re.sub(r"\D", "", phone or "")

    hits: list[ConflictHit] = []

    clients = db.scalars(
        select(Client).where(
            Client.organization_id == ctx.organization_id, Client.deleted_at.is_(None)
        )
    ).all()
    for c in clients:
        cname = _norm(c.full_name)
        # The person we'd be acting AGAINST is already our client -> hard conflict.
        if opp and cname == opp:
            hits.append(
                ConflictHit(
                    "block",
                    "adverse_to_existing_client",
                    f"The opposing party matches an existing client: {c.full_name}.",
                    c.full_name,
                )
            )
        # The prospective client already exists (not a conflict, but worth knowing).
        same_name = cname == name
        same_mail = bool(mail) and _norm(c.email) == mail
        same_phone = bool(ph) and re.sub(r"\D", "", c.phone or "") == ph
        if same_name or same_mail or same_phone:
            how = "name" if same_name else ("email" if same_mail else "phone")
            hits.append(
                ConflictHit(
                    "info",
                    "existing_client",
                    f"Prospective client matches an existing client ({how}): {c.full_name}.",
                    c.full_name,
                )
            )

    # Adverse parties on existing cases: have we previously been AGAINST this person?
    parties = db.scalars(
        select(CaseParty).where(CaseParty.organization_id == ctx.organization_id)
    ).all()
    for p in parties:
        if p.party_type.lower() in _ADVERSE_ROLES and _norm(p.name) == name and name:
            hits.append(
                ConflictHit(
                    "review",
                    "prior_adverse_party",
                    "We have previously been adverse to a party with this name "
                    f"('{p.name}'). Review before acting for them.",
                    p.name,
                )
            )

    # The free-text opposite_party stored on cases.
    if name:
        cases = db.scalars(
            select(Case).where(
                Case.organization_id == ctx.organization_id,
                Case.deleted_at.is_(None),
                Case.opposite_party.is_not(None),
            )
        ).all()
        for case in cases:
            if _norm(case.opposite_party) == name:
                hits.append(
                    ConflictHit(
                        "review",
                        "prior_adverse_party",
                        f"This person is recorded as the opposing party on case '{case.title}'.",
                        case.opposite_party or "",
                    )
                )

    severities = {h.severity for h in hits}
    if "block" in severities:
        level = "block"
    elif "review" in severities:
        level = "review"
    else:
        level = "clear"
    return ConflictReport(level=level, hits=hits)
