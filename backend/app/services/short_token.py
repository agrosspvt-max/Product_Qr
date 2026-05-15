"""Short-token generation for QR redirect URLs.

Tokens are 5–7 uppercase alphanumeric chars. They start at 5 chars; if
collision pressure becomes high during a batch, callers escalate to 6 then 7.
"""
from __future__ import annotations

import secrets
import string
from typing import Final

MIN_LENGTH: Final[int] = 5
MAX_LENGTH: Final[int] = 7
_ALPHABET: Final[str] = string.ascii_uppercase + string.digits
_SECRETS = secrets.SystemRandom()


def make_token(length: int = MIN_LENGTH) -> str:
    if not MIN_LENGTH <= length <= MAX_LENGTH:
        raise ValueError(f"length must be between {MIN_LENGTH} and {MAX_LENGTH}")
    return "".join(_SECRETS.choice(_ALPHABET) for _ in range(length))


def adaptive_length(attempt: int) -> int:
    """Escalate token length when collisions occur.

    Attempt 0..2 -> 5, 3..5 -> 6, otherwise -> 7.
    """
    if attempt < 3:
        return 5
    if attempt < 6:
        return 6
    return 7
