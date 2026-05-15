"""Unique product code generation.

Format:  [INITIALS:2][QTY:4][YYMM:4][SUFFIX:5]  ->  total 15 chars
All uppercase A-Z and digits 0-9 only.

Note: the original spec text said "exactly 17 chars" but the breakdown
(2+4+4+5) and example "VJ10002606AB12C" both resolve to 15 chars. The example
is the source of truth in this implementation; if you really need 17, raise
SUFFIX_LENGTH to 7 and re-run the schema migration (CHAR(15) -> CHAR(17)).
"""
from __future__ import annotations

import secrets
import string
from typing import Final

CODE_LENGTH: Final[int] = 15
SUFFIX_LENGTH: Final[int] = 5
_ALPHABET: Final[str] = string.ascii_uppercase + string.digits  # 36 chars
_SECRETS = secrets.SystemRandom()


def random_suffix(length: int = SUFFIX_LENGTH) -> str:
    """Cryptographically secure 5-char uppercase alphanumeric suffix."""
    return "".join(_SECRETS.choice(_ALPHABET) for _ in range(length))


def build_prefix(
    initials: str,
    quantity_code: str,
    manufacturing_month: int,
    manufacturing_year: int,
) -> str:
    """Build the 12-character deterministic prefix.

    initials must be 2 chars, quantity_code must be 4 chars.
    Year is reduced to its last 2 digits (YY) and month is zero-padded (MM).
    """
    initials = (initials or "").strip().upper()
    quantity_code = (quantity_code or "").strip().upper()
    if len(initials) != 2:
        raise ValueError(f"Product initials must be exactly 2 chars (got {len(initials)})")
    if len(quantity_code) != 4:
        raise ValueError(f"Quantity code must be exactly 4 chars (got {len(quantity_code)})")
    if not (1 <= manufacturing_month <= 12):
        raise ValueError("manufacturing_month must be between 1 and 12")
    if not (2000 <= manufacturing_year <= 2099):
        raise ValueError("manufacturing_year must be between 2000 and 2099")

    yy = f"{manufacturing_year % 100:02d}"
    mm = f"{manufacturing_month:02d}"
    prefix = f"{initials}{quantity_code}{yy}{mm}"
    if len(prefix) != CODE_LENGTH - SUFFIX_LENGTH:
        raise ValueError(f"Prefix length mismatch: {prefix!r}")
    return prefix


def make_code(prefix: str) -> str:
    """Compose a full 17-char code from a precomputed prefix + a fresh suffix."""
    code = f"{prefix}{random_suffix()}"
    if len(code) != CODE_LENGTH:
        raise ValueError(f"Generated code length is {len(code)}, expected {CODE_LENGTH}: {code!r}")
    return code


def validate_code(code: str) -> bool:
    """Sanity check — exactly 17 uppercase alphanumeric chars."""
    return (
        isinstance(code, str)
        and len(code) == CODE_LENGTH
        and all(c in _ALPHABET for c in code)
    )
