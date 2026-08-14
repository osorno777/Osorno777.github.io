from __future__ import annotations

import logging
from pathlib import Path

from translation_qa.models import Document
from translation_qa.passwords import load_pdf_passwords

logging.getLogger("pypdf").setLevel(logging.ERROR)
logging.getLogger("PyPDF2").setLevel(logging.ERROR)


class ExtractionError(RuntimeError):
    pass


def looks_like_pdf(path: Path) -> bool:
    """True only when the file actually starts with %PDF. Many KDP/XML sidecars are named .pdf."""
    if path.suffix.lower() != ".pdf":
        return False
    try:
        with path.open("rb") as handle:
            head = handle.read(16)
    except OSError:
        return False
    return head.startswith(b"%PDF")


def header_kind(path: Path) -> str:
    try:
        with path.open("rb") as handle:
            head = handle.read(16)
    except OSError:
        return "unreadable"
    if head.startswith(b"%PDF"):
        return "pdf"
    if head.lstrip().startswith(b"<?xml") or head.lstrip().startswith(b"<"):
        return "xml"
    if head.startswith(b"PK"):
        return "zip"
    return "other"


def extract_pdf(path: Path, passwords: list[str] | None = None) -> Document:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ExtractionError("pypdf is required. Run: pip install -r requirements.txt") from exc

    if not path.is_file():
        raise ExtractionError(f"PDF not found: {path}")
    if not looks_like_pdf(path):
        raise ExtractionError(
            f"Not a PDF ({header_kind(path)} header): {path}. Skipping this file."
        )

    reader = PdfReader(str(path))
    encrypted = bool(reader.is_encrypted)
    unlocked = not encrypted
    used_password = False
    if encrypted:
        for password in passwords or load_pdf_passwords():
            try:
                result = reader.decrypt(password)
            except Exception:
                continue
            if result:
                unlocked = True
                used_password = True
                break
        if not unlocked:
            raise ExtractionError(
                f"Encrypted PDF could not be opened: {path}. "
                "Set PDF_PASSWORDS in .env (semicolon-separated) and retry."
            )

    pages: list[str] = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        pages.append(_normalize_extracted(text))

    body = "\n\n".join(page for page in pages if page.strip())
    if not body.strip():
        raise ExtractionError(
            f"No extractable text in {path}. If this is a scanned PDF, install pymupdf "
            "or export a text-based PDF from InDesign/Word first."
        )

    return Document(
        path=path,
        text=body,
        pages=pages,
        title=path.stem,
        encrypted=encrypted,
        password_used=used_password,
    )


def extract_sample(path: Path, passwords: list[str] | None = None, pages: int = 2) -> str:
    """Read a few pages so discovery can guess language without loading the whole book."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    if not path.is_file():
        return ""
    if path.suffix.lower() == ".txt":
        try:
            return path.read_text(encoding="utf-8")[:4000]
        except OSError:
            return ""
    if path.suffix.lower() != ".pdf":
        return ""
    if not looks_like_pdf(path):
        return ""
    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            unlocked = False
            for password in passwords or load_pdf_passwords():
                try:
                    if reader.decrypt(password):
                        unlocked = True
                        break
                except Exception:
                    continue
            if not unlocked:
                return ""
        chunks: list[str] = []
        for page in list(reader.pages)[: max(1, pages)]:
            try:
                chunks.append(_normalize_extracted(page.extract_text() or ""))
            except Exception:
                continue
        return "\n".join(chunk for chunk in chunks if chunk.strip())
    except Exception:
        return ""


def extract_plain(path: Path, language: str = "und") -> Document:
    text = path.read_text(encoding="utf-8")
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    return Document(path=path, text=text, pages=paragraphs or [text], language=language, title=path.stem)


def _normalize_extracted(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u00ad", "")  # soft hyphen
    text = text.replace("\ufeff", "")
    lines = [" ".join(line.split()) for line in text.split("\n")]
    return "\n".join(line for line in lines if line)
