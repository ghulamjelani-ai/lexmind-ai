"""TOTP-based multi-factor authentication.

The TOTP secret is stored encrypted at rest (mfa_secret_enc). Enrolment sets
the secret but does not enable MFA until the user proves possession by
submitting a valid code (activate).
"""

from __future__ import annotations

import pyotp
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.crypto import decrypt_str, encrypt_str
from app.models.user import User


class MFAError(Exception):
    pass


def enroll(db: Session, user: User) -> tuple[str, str]:
    """Generate a fresh secret (not yet enabled). Returns (secret, otpauth_uri)."""
    settings = get_settings()
    secret = pyotp.random_base32()
    user.mfa_secret_enc = encrypt_str(secret)
    db.flush()
    uri = pyotp.TOTP(secret).provisioning_uri(
        name=user.email, issuer_name=settings.mfa_issuer
    )
    return secret, uri


def _verify_code(user: User, code: str) -> bool:
    if not user.mfa_secret_enc:
        return False
    try:
        secret = decrypt_str(user.mfa_secret_enc)
    except Exception:
        return False
    # valid_window=1 tolerates slight clock drift (±30s).
    return pyotp.TOTP(secret).verify(code, valid_window=1)


def activate(db: Session, user: User, code: str) -> None:
    """Enable MFA after the user proves possession of the secret."""
    if not user.mfa_secret_enc:
        raise MFAError("Not enrolled; call enroll first")
    if not _verify_code(user, code):
        raise MFAError("Invalid code")
    user.mfa_enabled = True
    db.flush()


def disable(db: Session, user: User, code: str) -> None:
    if not user.mfa_enabled:
        return
    if not _verify_code(user, code):
        raise MFAError("Invalid code")
    user.mfa_enabled = False
    user.mfa_secret_enc = None
    db.flush()


def verify_login(user: User, code: str | None) -> bool:
    """At login: a user with MFA enabled must supply a valid code."""
    if not user.mfa_enabled:
        return True
    if not code:
        return False
    return _verify_code(user, code)
