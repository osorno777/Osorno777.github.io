from __future__ import annotations

import os
from pathlib import Path


def load_pdf_passwords(extra: list[str] | None = None) -> list[str]:
    """Load PDF passwords from the environment. Never hardcode production passwords."""
    raw = os.environ.get("PDF_PASSWORDS", "")
    values = [part.strip() for part in raw.replace("\n", ";").split(";") if part.strip()]
    if extra:
        values.extend(item for item in extra if item)
    # Preserve order while dropping duplicates.
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            unique.append(value)
    return unique


def load_dotenv(path: Path | None = None) -> None:
    """Minimal .env loader so Windows users can keep passwords off the command line."""
    candidate = path or Path.cwd() / ".env"
    if not candidate.is_file():
        package_dir = Path(__file__).resolve().parent.parent / ".env"
        if package_dir.is_file():
            candidate = package_dir
        else:
            return
    for line in candidate.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
