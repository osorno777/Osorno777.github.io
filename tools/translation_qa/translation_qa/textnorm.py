from __future__ import annotations

import re
import unicodedata


def fold(text: str) -> str:
    """Lowercase, strip accents, and collapse punctuation so titles match across languages."""
    normalized = unicodedata.normalize("NFKD", text or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", ascii_text.lower()).strip()


def isbn_digits(text: str) -> str:
    return re.sub(r"[^0-9Xx]", "", text or "")
