from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from translation_qa.catalog import BOOKS, BOOKS_BY_ID, FOREIGN_TITLE_ALIASES, NUMBERED_STEMS, SHORT_CODES
from translation_qa.extract import extract_sample, header_kind, looks_like_epub, looks_like_pdf
from translation_qa.languages import LANGUAGE_NAMES, NAME_TO_CODE, detect_language_from_text
from translation_qa.textnorm import fold, isbn_digits

_SKIP_NAME_MARKERS = (
    "do-not-use",
    "do_not_use",
    "biodup",
    "draft-discard",
    "not for sale",
    "dustjacket",
    "nohyph",
    "silence_log",
    "objecterror",
)

_SKIP_PATH_MARKERS = (
    "_freedom_data",
    "_nohyph",
    "audiobooks",
    "cell phone saves",
    "backup_pre_kdp",
    "ea games",
    "the sims 2",
    "the sims",
    "docs 1990s",
    "olders docs",
    "agent_workflows",
    "literary agent",
    "indexing use",
)

_ENGLISH_MARKERS = (
    "english",
    "(en)",
    "_en.",
    "_en_",
    "_en ",
    "_en(",
    "-en.",
    "-en-",
    "-en ",
    " complete",
    "(complete)",
    "interior",
)

# ISO codes only count in filename language slots (_ES.pdf, _AF_2026, _en (1)),
# not mid-title words such as life_in_chile or Sentenced_to_the_Future.
_ISO_SLOT_RE = re.compile(
    r"(?:^|[_\-.])(zh[-_](?:cn|tw|hk)|pt[-_]br|[a-z]{2,3})"
    r"(?=_2026|-2026|_ebook|_paperback|\.[a-z]{3,4}$|[()\s])",
    re.I,
)


@dataclass(frozen=True)
class BookPair:
    english: Path
    translated: Path
    language: str
    book_id: str


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def infer_language(path: Path, passwords: list[str] | None = None, *, peek: bool = False) -> str:
    # Filename + immediate parent only. Scanning every ancestor folder
    # misfires when a pytest tmp dir or unrelated path contains "spanish".
    haystack = _local_haystack(path)
    folded = fold(haystack)
    for name, code in sorted(NAME_TO_CODE.items(), key=lambda item: -len(item[0])):
        if name == "english" or len(name) < 4:
            continue
        if re.search(rf"\b{re.escape(name)}\b", haystack):
            return code
        name_fold = fold(name)
        if name_fold and len(name_fold) >= 5 and re.search(rf"\b{re.escape(name_fold)}\b", folded):
            return code
    codes = [_normalize_lang_part(part) for part in _language_tag_parts(path)]
    codes = [code for code in codes if code]
    non_en = [code for code in codes if code != "en"]
    if non_en:
        return non_en[0]
    if "en" in codes:
        return "en"
    if _looks_english(path):
        return "en"
    if peek:
        try:
            sample = extract_sample(path, passwords=passwords)
            guessed = detect_language_from_text(sample)
            if guessed != "und":
                return guessed
        except Exception:
            return "und"
    return "und"


def _normalize_lang_part(part: str) -> str | None:
    part = part.lower().replace("_", "-")
    if part in {"zh-cn", "cn"}:
        return "zh"
    if part in {"zh-tw", "tw", "zh-hk", "hk"}:
        return "zh-tw"
    if part in {"pt-br", "br"}:
        return "pt-br"
    if part in LANGUAGE_NAMES:
        return part
    return None


def _language_tag_parts(path: Path) -> list[str]:
    """ISO codes only count as language tags, not as words like Spanish 'de'."""
    tagged: list[str] = []
    blob = path.name.lower()
    for compound in ("zh-hk", "zh_hk", "zh-cn", "zh_cn", "zh-tw", "zh_tw", "pt-br", "pt_br"):
        if compound in blob:
            tagged.append(compound)
    tagged.extend(part.lower().replace("_", "-") for part in _ISO_SLOT_RE.findall(blob))
    tagged.extend(re.findall(r"\(([a-z]{2,3})\)", blob))
    name = path.parent.name.lower().strip()
    if re.fullmatch(r"[a-z]{2,3}", name) or name in LANGUAGE_NAMES or name in NAME_TO_CODE:
        tagged.append(NAME_TO_CODE.get(name, name))
    if name in {"zh-cn", "zh_cn", "zh-tw", "zh_tw", "zh-hk", "zh_hk", "pt-br", "pt_br"}:
        tagged.append(name)
    return tagged


def infer_book_id(path: Path) -> str:
    catalog_id = catalog_book_id(path)
    if catalog_id:
        return catalog_id
    stem = path.stem.lower()
    stem = re.sub(r"\((complete|2026|en|english|interior|final|v\d+)\)", " ", stem, flags=re.I)
    stem = re.sub(r"\b(complete|english|en|interior|final|biodup|v\d+|pp|\d+pp)\b", " ", stem, flags=re.I)
    stem = re.sub(r"[^a-z0-9]+", " ", stem).strip()
    tokens = [token for token in stem.split() if token not in LANGUAGE_NAMES and len(token) > 1]
    return " ".join(tokens[:8])


def catalog_book_id(path: Path) -> str | None:
    stem = path.stem.lower()
    for prefix, book_id in NUMBERED_STEMS:
        if re.match(rf"^{re.escape(prefix)}[_ \-]", stem):
            return book_id

    haystack = fold(f"{path.stem} {path.parent.name}")
    digits = isbn_digits(f"{path.stem} {path.name}")
    for book in BOOKS:
        for isbn in book.isbns:
            if isbn and isbn in digits:
                return book.id

    best_id: str | None = None
    best_score = 0
    for book in BOOKS:
        score = 0
        for alias in book.aliases:
            alias_fold = fold(alias)
            if not alias_fold:
                continue
            if alias_fold == haystack or f" {alias_fold} " in f" {haystack} ":
                score = max(score, 80 + len(alias_fold))
            elif alias_fold in haystack and len(alias_fold) >= 12:
                score = max(score, 50 + len(alias_fold))
        if score > best_score:
            best_id = book.id
            best_score = score

    if best_score >= 50:
        return _prefer_specific_btc(best_id, haystack)

    tokens = set(haystack.split())
    for code, book_id in SHORT_CODES.items():
        if code in tokens:
            return _prefer_specific_btc(book_id, haystack)
    return None


def collect_pdfs(folders: list[Path]) -> list[Path]:
    files: list[Path] = []
    seen: set[str] = set()
    for folder in folders:
        if not folder.is_dir():
            continue
        for root, dirnames, filenames in os.walk(folder):
            dirnames[:] = [name for name in dirnames if not _skip_path(Path(root) / name)]
            if _skip_path(Path(root)):
                dirnames[:] = []
                continue
            for name in filenames:
                path = Path(root) / name
                if path.suffix.lower() not in {".pdf", ".txt", ".epub"}:
                    continue
                if _skip_path(path):
                    continue
                key = str(path).lower()
                if key in seen:
                    continue
                seen.add(key)
                files.append(path)
    return files


def select_english_sources(config: dict) -> list[Path]:
    explicit = [Path(item) for item in config.get("english_sources", []) if item]
    folders = _config_folders(config, "english_dirs", "translations_dirs", "translations_dir")
    found = [path for path in collect_pdfs(folders) if not _should_skip(path)]
    ranked: dict[str, Path] = {}
    for path in found:
        book_id = catalog_book_id(path)
        if not book_id:
            continue
        if _foreign_title_alias(path) or _has_non_english_language_tag(path):
            continue
        language = infer_language(path)
        if language not in {"en", "und"}:
            continue
        current = ranked.get(book_id)
        if current is None or _english_rank(path) > _english_rank(current):
            ranked[book_id] = path
    by_id = dict(ranked)
    for path in explicit:
        if not path:
            continue
        book_id = catalog_book_id(path) or infer_book_id(path)
        if book_id:
            by_id[book_id] = path
    return [path for path in by_id.values() if path]


def discover_pairs(
    config: dict, passwords: list[str] | None = None, peek: bool | None = None
) -> list[BookPair]:
    english_sources = select_english_sources(config)
    english_by_id = {
        (catalog_book_id(path) or infer_book_id(path)): path
        for path in english_sources
        if catalog_book_id(path) or infer_book_id(path)
    }
    if peek is None:
        peek = bool(config.get("peek_language", False))

    candidates = list(_explicit_translations(config))
    candidates.extend(collect_pdfs(_config_folders(config, "translations_dirs", "translations_dir")))

    pairs: list[BookPair] = []
    seen: set[tuple[str, str]] = set()
    for translated in candidates:
        try:
            pair = _pair_for_file(translated, english_by_id, passwords, peek)
            if pair is None:
                continue
            key = (
                str(pair.english.resolve()) if pair.english.exists() else str(pair.english),
                str(pair.translated),
            )
            if key in seen:
                continue
            seen.add(key)
            pairs.append(pair)
        except Exception as exc:
            print(f"  skip {translated}: {exc}", file=sys.stderr)
            continue
    pairs = _prefer_ebook_pairs(pairs)
    pairs.sort(key=lambda item: (item.book_id, item.language, str(item.translated)))
    return pairs


def translation_candidates(config: dict) -> list[Path]:
    files = list(_explicit_translations(config))
    files.extend(collect_pdfs(_config_folders(config, "translations_dirs", "translations_dir")))
    return files


def unmatched_translations(
    config: dict, passwords: list[str] | None = None, peek: bool | None = None
) -> list[tuple[Path, str]]:
    english_by_id = _english_by_id(config)
    pairs = discover_pairs(config, passwords, peek=peek)
    paired = {
        pair.translated.resolve() if pair.translated.exists() else pair.translated
        for pair in pairs
    }
    leftover: list[tuple[Path, str]] = []
    for path in translation_candidates(config):
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if resolved in paired:
            continue
        leftover.append((path, _skip_reason(path, english_by_id, pairs, passwords)))
    return leftover


def inventory_rows(
    config: dict, passwords: list[str] | None = None, peek: bool | None = None
) -> list[dict[str, str]]:
    """Describe every PDF the config can see, whether or not it paired."""
    if peek is None:
        peek = False
    rows: list[dict[str, str]] = []
    for path in select_english_sources(config):
        rows.append(
            {
                "role": "english",
                "book_id": catalog_book_id(path) or infer_book_id(path),
                "language": "en",
                "path": str(path),
                "note": "",
            }
        )
    english_by_id = _english_by_id(config)
    pairs = discover_pairs(config, passwords, peek=peek)
    paired = {
        pair.translated.resolve() if pair.translated.exists() else pair.translated
        for pair in pairs
    }
    for path in translation_candidates(config):
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        language = infer_language(path, passwords=passwords, peek=peek)
        book_id = _match_book_id(path, english_by_id) or catalog_book_id(path) or infer_book_id(path)
        if resolved in paired:
            note = "paired"
            role = "translation"
        else:
            note = _skip_reason(path, english_by_id, pairs, passwords)
            role = "unmatched"
        rows.append(
            {
                "role": role,
                "book_id": book_id or "",
                "language": language,
                "path": str(path),
                "note": note,
            }
        )
    return rows


def _english_by_id(config: dict) -> dict[str, Path]:
    return {
        (catalog_book_id(path) or infer_book_id(path)): path
        for path in select_english_sources(config)
        if catalog_book_id(path) or infer_book_id(path)
    }


def _explicit_translations(config: dict) -> list[Path]:
    return [Path(item) for item in config.get("reference_translations", []) if item]


def _config_folders(config: dict, *keys: str) -> list[Path]:
    folders: list[Path] = []
    seen: set[str] = set()
    for key in keys:
        value = config.get(key)
        items = value if isinstance(value, list) else [value] if value else []
        for item in items:
            path = Path(item)
            marker = str(path).lower()
            if marker in seen:
                continue
            seen.add(marker)
            folders.append(path)
    return folders


def _pair_for_file(
    translated: Path,
    english_by_id: dict[str, Path],
    passwords: list[str] | None,
    peek: bool,
) -> BookPair | None:
    if _should_skip(translated):
        return None
    if not _is_translation_candidate(translated):
        return None
    language = infer_language(translated, passwords=passwords, peek=peek)
    if language == "en":
        return None
    book_id = _match_book_id(translated, english_by_id)
    if not book_id:
        return None
    english_path = english_by_id[book_id]
    if _same_file(translated, english_path):
        return None
    return BookPair(
        english=english_path,
        translated=translated,
        language=language,
        book_id=book_id,
    )


def _is_translation_candidate(path: Path) -> bool:
    codes = [_normalize_lang_part(part) for part in _language_tag_parts(path)]
    if "en" in codes and not any(code and code != "en" for code in codes):
        return False
    if _has_non_english_language_tag(path):
        return True
    if _foreign_title_alias(path):
        return True
    return False


def _skip_reason(
    path: Path,
    english_by_id: dict[str, Path],
    pairs: list[BookPair],
    passwords: list[str] | None = None,
) -> str:
    if _skip_path(path):
        return "skipped junk folder"
    if path.suffix.lower() == ".pdf" and path.is_file() and not looks_like_pdf(path):
        return f"not a PDF ({header_kind(path)} header)"
    if path.suffix.lower() == ".epub" and path.is_file() and not looks_like_epub(path):
        return f"not an EPUB ({header_kind(path)} header)"
    if _should_skip(path):
        return "skipped DO-NOT-USE/BIODUP"
    language = infer_language(path, passwords=passwords, peek=bool(passwords is not None))
    book_id = catalog_book_id(path)
    if "paperback" in path.name.lower() and book_id:
        for pair in pairs:
            if pair.book_id == book_id and pair.language == language and "ebook" in pair.translated.name.lower():
                return "skipped paperback; ebook exists for this language"
    if language == "en":
        return "looks like English, not a translation"
    if not _is_translation_candidate(path):
        return "English interior/filename without a language tag"
    if language == "und" and _looks_english(path):
        return "English interior/filename without a language tag"
    if not _match_book_id(path, english_by_id):
        return "no matching English title"
    if book_id:
        for pair in pairs:
            if pair.book_id == book_id and pair.language == language:
                return "duplicate; another file already paired for this language"
    return "already paired or same file"


def _match_book_id(translated: Path, english_by_id: dict[str, Path]) -> str | None:
    catalog_id = catalog_book_id(translated)
    if not catalog_id:
        return None
    return _resolve_english_id(catalog_id, english_by_id)


def _resolve_english_id(book_id: str, english_by_id: dict[str, Path]) -> str | None:
    if book_id in english_by_id:
        return book_id
    book = BOOKS_BY_ID.get(book_id)
    if book and book.fallback and book.fallback in english_by_id:
        return book.fallback
    if book and book.family:
        for other_id in english_by_id:
            other = BOOKS_BY_ID.get(other_id)
            if other and other.family == book.family:
                return other_id
    return None


def _prefer_specific_btc(book_id: str | None, haystack: str) -> str | None:
    if not book_id:
        return None
    if book_id != "bearing-the-cross" and not book_id.startswith("bearing-the-cross"):
        return book_id
    part_hits = (
        ("bearing-the-cross-1", ("book one", "book 1", "btc1", "valparaiso part 1")),
        ("bearing-the-cross-2", ("book two", "book 2", "btc2", "valparaiso part 2")),
        ("bearing-the-cross-3", ("book three", "book 3", "btc3", "rancagua", "valparaiso part 3")),
        ("bearing-the-cross-4", ("book four", "book 4", "btc4", "casablanca part 1")),
        ("bearing-the-cross-5", ("book five", "book 5", "btc5", "casablanca part 2")),
    )
    for part_id, markers in part_hits:
        if any(fold(marker) in haystack for marker in markers):
            return part_id
    return book_id


def _prefer_ebook_pairs(pairs: list[BookPair]) -> list[BookPair]:
    best: dict[tuple[str, str], BookPair] = {}
    for pair in pairs:
        key = (pair.book_id, pair.language)
        current = best.get(key)
        if current is None or _translation_rank(pair.translated) > _translation_rank(current.translated):
            best[key] = pair
    return list(best.values())


def _local_haystack(path: Path) -> str:
    return f"{path.stem} {path.parent.name}".lower()


def _has_non_english_language_tag(path: Path) -> bool:
    for part in _language_tag_parts(path):
        mapped = _normalize_lang_part(part)
        if mapped and mapped != "en":
            return True
    haystack = fold(f"{path.stem} {path.parent.name}")
    raw = f"{path.stem} {path.parent.name}".lower()
    for name, code in NAME_TO_CODE.items():
        if code == "en" or len(name) < 4:
            continue
        if re.search(rf"\b{re.escape(name)}\b", raw):
            return True
        name_fold = fold(name)
        if name_fold and len(name_fold) >= 5 and re.search(rf"\b{re.escape(name_fold)}\b", haystack):
            return True
    return False


def _foreign_title_alias(path: Path) -> bool:
    stem = fold(path.stem)
    return any(fold(alias) in stem for alias in FOREIGN_TITLE_ALIASES if len(fold(alias)) >= 6)


def _looks_english(path: Path) -> bool:
    blob = path.stem.lower()
    if any(marker in blob for marker in _ENGLISH_MARKERS):
        return True
    tokens = set(re.findall(r"[a-z]+", blob))
    englishish = tokens & {
        "the", "and", "of", "behind", "walls", "bearing", "cross", "suffering",
        "unjustly", "complete", "interior", "primer", "policy", "economics",
        "bible", "government", "christian", "theology", "chile", "life",
        "dissertation", "finance", "austrian", "institutional", "sentenced",
        "future", "surviving", "chilean", "justice", "defending", "choice",
        "public", "personal", "augmented",
    }
    language_hint = any(
        token in LANGUAGE_NAMES or token in NAME_TO_CODE
        for token in re.split(r"[ .()\[\]_/-]+", blob)
        if token not in {"the", "and", "of", "in", "en"}
    )
    return len(englishish) >= 2 and not language_hint


def _english_rank(path: Path) -> int:
    name = path.name.lower()
    blob = str(path).lower().replace("\\", "/")
    score = 0
    if re.search(r"(^|[_\-])en([_\-]|$)", name) or "_en_" in name:
        score += 25
    if "ebook" in name:
        score += 20
    if "kdp_by_isbn" in blob:
        score += 15
    if re.match(r"^\d{2}[a-z]?[_-]", name):
        score += 12
    if "complete" in name:
        score += 8
    if "final" in name and "do-not-use" not in name:
        score += 4
    if "2026" in name:
        score += 2
    if "paperback" in name:
        score -= 18
    if "interior" in name:
        score -= 25
    if "cell phone" in blob or "backup" in blob or "nohyph" in blob:
        score -= 40
    if path.suffix.lower() == ".txt":
        score -= 30
    if "dustjacket" in name or "postcard" in name:
        score -= 50
    if any(word in name for word in ("lecture", "outline", "overview", "observaciones")):
        score -= 40
    if _foreign_title_alias(path):
        score -= 80
    return score


def _translation_rank(path: Path) -> int:
    name = path.name.lower()
    blob = str(path).lower().replace("\\", "/")
    score = 0
    if "ebook" in name:
        score += 20
    if "kdp_by_isbn" in blob:
        score += 15
    if "paperback" in name:
        score -= 18
    if "cell phone" in blob or "backup" in blob or "nohyph" in blob:
        score -= 40
    if path.suffix.lower() == ".txt":
        score -= 30
    return score


def _should_skip(path: Path) -> bool:
    name = path.name.lower()
    if any(marker in name for marker in _SKIP_NAME_MARKERS):
        return True
    if _skip_path(path):
        return True
    if path.suffix.lower() == ".pdf" and path.is_file() and not looks_like_pdf(path):
        return True
    if path.suffix.lower() == ".epub" and path.is_file() and not looks_like_epub(path):
        return True
    return False


def _skip_path(path: Path) -> bool:
    blob = str(path).lower().replace("\\", "/")
    return any(marker in blob for marker in _SKIP_PATH_MARKERS)


def _same_file(left: Path, right: Path) -> bool:
    try:
        return left.resolve() == right.resolve()
    except OSError:
        return left == right
