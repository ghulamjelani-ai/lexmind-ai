"""Symmetric field encryption for secrets at rest (e.g. MFA TOTP secrets).

Uses Fernet (AES-128-CBC + HMAC). The key comes from settings.encryption_key
in production. If unset, a deterministic DEV-ONLY key is used and a warning is
logged — never rely on this in production.
"""

from __future__ import annotations

import base64
import hashlib
import logging

from cryptography.fernet import Fernet

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_DEV_WARNING_EMITTED = False


def _dev_key() -> bytes:
    global _DEV_WARNING_EMITTED
    if not _DEV_WARNING_EMITTED:
        logger.warning(
            "ENCRYPTION_KEY is not set — using an insecure dev key. "
            "Set ENCRYPTION_KEY in production."
        )
        _DEV_WARNING_EMITTED = True
    digest = hashlib.sha256(b"lexmind-dev-insecure-key").digest()
    return base64.urlsafe_b64encode(digest)


def _fernet() -> Fernet:
    key = get_settings().encryption_key
    if key:
        return Fernet(key.encode() if isinstance(key, str) else key)
    return Fernet(_dev_key())


def encrypt_str(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_str(ciphertext: str) -> str:
    return _fernet().decrypt(ciphertext.encode("utf-8")).decode("utf-8")


def generate_key() -> str:
    """Helper to mint a production ENCRYPTION_KEY: `python -c ...`."""
    return Fernet.generate_key().decode("utf-8")
