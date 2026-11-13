"""Email OTP verification for signup.

A 6-digit, single-use, time-limited code is emailed to the address being
registered. The organization is created ONLY after the code is verified, so an
account can never be created for an email the requester does not control.

Only the SHA-256 hash of the code is stored. Attempts are capped.
"""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, hash_token
from app.models.email_verification import EmailVerification
from app.models.organization import Organization
from app.models.user import User
from app.services.org_service import ProvisioningError, provision_organization

OTP_TTL_MINUTES = 10
MAX_ATTEMPTS = 5
PURPOSE = "signup"


class VerificationError(Exception):
    pass


def _now() -> datetime:
    return datetime.now(UTC)


def _gen_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def create_signup_otp(
    db: Session,
    *,
    org_name: str,
    org_slug: str,
    owner_name: str,
    owner_email: str,
    owner_password: str,
) -> str:
    """Validate the pending signup, store a hashed OTP + payload, and return the
    plaintext code (the caller emails it). Raises VerificationError if the slug
    is taken."""
    slug = org_slug.strip().lower()
    if db.scalar(select(Organization).where(Organization.slug == slug)):
        raise VerificationError(f"Chamber ID '{slug}' is already taken. Choose another.")

    # Invalidate any earlier pending codes for this email+purpose.
    for row in db.scalars(
        select(EmailVerification).where(
            EmailVerification.email == owner_email.lower(),
            EmailVerification.purpose == PURPOSE,
            EmailVerification.consumed_at.is_(None),
        )
    ).all():
        row.consumed_at = _now()

    code = _gen_code()
    db.add(
        EmailVerification(
            email=owner_email.lower(),
            purpose=PURPOSE,
            code_hash=hash_token(code),
            payload={
                "org_name": org_name.strip(),
                "org_slug": slug,
                "owner_name": owner_name.strip(),
                "password_hash": hash_password(owner_password),
            },
            expires_at=_now() + timedelta(minutes=OTP_TTL_MINUTES),
            attempts=0,
        )
    )
    db.flush()
    return code


def verify_signup(db: Session, email: str, code: str) -> tuple[Organization, User]:
    """Verify the OTP and provision the organization. Raises VerificationError."""
    row = db.scalar(
        select(EmailVerification)
        .where(
            EmailVerification.email == email.lower(),
            EmailVerification.purpose == PURPOSE,
            EmailVerification.consumed_at.is_(None),
        )
        .order_by(EmailVerification.created_at.desc())
    )
    if row is None:
        raise VerificationError("No pending verification. Please start again.")

    exp = row.expires_at if row.expires_at.tzinfo else row.expires_at.replace(tzinfo=UTC)
    if exp < _now():
        raise VerificationError("This code has expired. Please request a new one.")
    if row.attempts >= MAX_ATTEMPTS:
        raise VerificationError("Too many attempts. Please request a new code.")

    row.attempts += 1
    db.flush()
    if hash_token(code.strip()) != row.code_hash:
        raise VerificationError("Incorrect code. Please try again.")

    row.consumed_at = _now()
    p = row.payload or {}
    try:
        org, owner = provision_organization(
            db,
            org_name=p["org_name"],
            org_slug=p["org_slug"],
            owner_email=email.lower(),
            owner_name=p["owner_name"],
            owner_password_hash=p["password_hash"],
        )
    except ProvisioningError as exc:
        raise VerificationError(str(exc)) from exc
    return org, owner
