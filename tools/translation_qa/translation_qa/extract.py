from __future__ import annotations

import logging
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

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


def looks_like_epub(path: Path) -> bool:
    if path.suffix.lower() != ".epub":
        return False
    try:
        with zipfile.ZipFile(path) as archive:
            kind = archive.read("mimetype").decode("ascii", "ignore").strip()
        return kind.startswith("application/epub")
    except Exception:
        return False


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
    """Read a few pages so discovery can guess language without loading the whole book.

    Never raises: junk XML, truncated PDFs, and Windows-1252 .txt files must not abort a catalog scan.
    """
    try:
        if not path.is_file():
            return ""
        if path.suffix.lower() == ".txt":
            return read_text_lenient(path, limit=4000)
        if path.suffix.lower() == ".epub":
            if not looks_like_epub(path):
                return ""
            return extract_epub(path).text[:4000]
        if path.suffix.lower() != ".pdf" or not looks_like_pdf(path):
            return ""
        from pypdf import PdfReader

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


def extract_epub(path: Path, language: str = "und") -> Document:
    """Pull text from an EPUB (the format the Alertness Books reader serves)."""
    if not path.is_file():
        raise ExtractionError(f"EPUB not found: {path}")
    if not looks_like_epub(path):
        raise ExtractionError(f"Not an EPUB ({header_kind(path)} header): {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            rootfile = _epub_rootfile(archive)
            hrefs = _epub_spine_hrefs(archive, rootfile)
            pages: list[str] = []
            for href in hrefs:
                try:
                    raw = archive.read(href)
                except KeyError:
                    continue
                pages.append(_html_to_text(raw.decode("utf-8", "ignore")))
    except zipfile.BadZipFile as exc:
        raise ExtractionError(f"Not an EPUB zip: {path}") from exc
    body = "\n\n".join(page for page in pages if page.strip())
    if not body.strip():
        raise ExtractionError(f"No extractable text in {path}")
    return Document(path=path, text=body, pages=pages, language=language, title=path.stem)


def _epub_rootfile(archive: zipfile.ZipFile) -> str:
    xml = ET.fromstring(archive.read("META-INF/container.xml"))
    ns = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}
    node = xml.find(".//c:rootfile", ns)
    if node is None:
        node = xml.find(".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile")
    href = node.get("full-path") if node is not None else None
    if not href:
        raise ExtractionError("EPUB container.xml has no rootfile")
    return href


def _epub_spine_hrefs(archive: zipfile.ZipFile, rootfile: str) -> list[str]:
    opf = ET.fromstring(archive.read(rootfile))
    ns = {"p": "http://www.idpf.org/2007/opf"}
    manifest = {
        item.get("id"): item.get("href")
        for item in opf.findall(".//{http://www.idpf.org/2007/opf}item")
        + opf.findall(".//p:item", ns)
        if item.get("id") and item.get("href")
    }
    refs = opf.findall(".//{http://www.idpf.org/2007/opf}itemref") + opf.findall(".//p:itemref", ns)
    base = str(Path(rootfile).parent).replace("\\", "/").rstrip(".")
    hrefs: list[str] = []
    seen: set[str] = set()
    for ref in refs:
        href = manifest.get(ref.get("idref") or "")
        if not href:
            continue
        if base and base not in {".", ""}:
            joined = f"{base}/{href}".replace("//", "/")
        else:
            joined = href
        if joined not in seen:
            seen.add(joined)
            hrefs.append(joined)
    return hrefs


def _html_to_text(markup: str) -> str:
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", markup)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p>", "\n\n", text)
    text = re.sub(r"(?i)</h[1-6]>", "\n\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return _normalize_extracted(text)


def extract_plain(path: Path, language: str = "und") -> Document:
    text = read_text_lenient(path)
    if not text.strip():
        raise ExtractionError(f"No extractable text in {path}")
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    return Document(path=path, text=text, pages=paragraphs or [text], language=language, title=path.stem)


def read_text_lenient(path: Path, limit: int | None = None) -> str:
    """Decode a .txt file without crashing on Windows-1252 or Latin-1 bytes."""
    try:
        data = path.read_bytes()
    except OSError:
        return ""
    if b"\x00" in data[:8192]:
        return ""
    if limit is not None:
        data = data[: max(limit * 4, 8000)]
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            text = data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        return ""
    text = _normalize_extracted(text)
    return text[:limit] if limit is not None else text


def _normalize_extracted(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u00ad", "")  # soft hyphen
    text = text.replace("\ufeff", "")
    lines = [" ".join(line.split()) for line in text.split("\n")]
    return "\n".join(line for line in lines if line)
