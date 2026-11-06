"""Password hashing (Argon2id) and opaque session-token helpers.

Session tokens: a long random string is given to the client in an httpOnly
cookie; only its SHA-256 hash is stored server-side, so the database never
holds a usable token.
"""

from __future__ import annotations

import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Argon2id is the default variant for argon2-cffi's PasswordHasher.
_ph = PasswordHasher()

SESSION_TOKEN_BYTES = 32


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _ph.verify(password_hash, password)
    except VerifyMismatchError:
        return False
    except Exception:
        # Malformed hash, etc. — treat as a failed verification, never raise.
        return False


def needs_rehash(password_hash: str) -> bool:
    try:
        return _ph.check_needs_rehash(password_hash)
    except Exception:
        return False


def generate_session_token() -> str:
    """A URL-safe opaque token handed to the client."""
    return secrets.token_urlsafe(SESSION_TOKEN_BYTES)


def hash_token(token: str) -> str:
    """Deterministic hash for storing/looking up a session or invite token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
