"""Shared input validators and normalisers for user-supplied data.

The server is the authoritative guard — the frontend mirrors these rules for a
better experience, but can be bypassed, so every schema validates here too.
Exposed as Pydantic ``Annotated`` types so fields stay declarative and consistent.
"""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import BeforeValidator, EmailStr

_NON_DIGIT = re.compile(r"\D")
_PHONE_STRIP = re.compile(r"[\s\-().]")
_PHONE_OK = re.compile(r"\+?\d{7,15}")


def blank_to_none(value: object) -> object:
    """Treat an empty/whitespace-only string as an omitted (None) value."""
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


def normalize_cnic(value: object) -> object:
    """Pakistani CNIC: must contain exactly 13 digits (dashes/spaces allowed).
    The user's formatting is preserved; empty becomes None; a wrong length
    raises a clear error."""
    if not isinstance(value, str):
        return value
    trimmed = value.strip()
    if trimmed == "":
        return None
    digits = _NON_DIGIT.sub("", trimmed)
    if len(digits) != 13:
        raise ValueError("CNIC must be 13 digits (e.g. 35202-1234567-1).")
    return trimmed


def normalize_phone(value: object) -> object:
    """Validate a phone number leniently: ignoring spaces, dashes and brackets it
    must be 7–15 digits with an optional leading '+'. The user's formatting is
    preserved; empty becomes None."""
    if not isinstance(value, str):
        return value
    trimmed = value.strip()
    if trimmed == "":
        return None
    cleaned = _PHONE_STRIP.sub("", trimmed)
    if not _PHONE_OK.fullmatch(cleaned):
        raise ValueError("Enter a valid phone number (7–15 digits, optional leading +).")
    return trimmed


# Reusable optional field types for schemas.
Cnic = Annotated[str | None, BeforeValidator(normalize_cnic)]
Phone = Annotated[str | None, BeforeValidator(normalize_phone)]
OptionalEmail = Annotated[EmailStr | None, BeforeValidator(blank_to_none)]
