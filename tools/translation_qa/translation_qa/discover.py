from __future__ import annotations

import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from translation_qa.catalog import BOOKS, BOOKS_BY_ID, SHORT_CODES
from translation_qa.extract import extract_sample
from translation_qa.languages import LANGUAGE_NAMES, NAME_TO_CODE, detect_language_from_text
from translation_qa.textnorm import fold, isbn_digits

_SKIP_NAME_MARKERS = (
    "do-not-use",
    "do_not_use",
    "biodup",
    "draft-discard",
    "not for sale",
)

_ENGLISH_MARKERS = (
    "english",
    "(en)",
    "_en.",
    "-en.",
    " complete",
    "(complete)",
    "interior",
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
    haystack = " ".join(_path_tokens(path))
    folded = fold(haystack)
    for name, code in sorted(NAME_TO_CODE.items(), key=lambda item: -len(item[0])):
        if name == "english" or len(name) < 4:
            continue
        if re.search(rf"\b{re.escape(name)}\b", haystack):
            return code
        name_fold = fold(name)
        if name_fold and len(name_fold) >= 5 and re.search(rf"\b{re.escape(name_fold)}\b", folded):
            return code
    for part in _language_tag_parts(path):
        if part in {"zh-cn", "zh_cn", "cn"}:
            return "zh"
        if part in {"zh-tw", "zh_tw", "tw"}:
            return "zh-tw"
        if part in {"pt-br", "pt_br", "br"}:
            return "pt-br"
        if part in LANGUAGE_NAMES and part != "en":
            return part
    if _looks_english(path):
        return "en"
    if peek:
        sample = extract_sample(path, passwords=passwords)
        guessed = detect_language_from_text(sample)
        if guessed != "und":
            return guessed
    return "und"


def _language_tag_parts(path: Path) -> list[str]:
    """ISO codes only count as language tags, not as words like Spanish 'de'."""
    tagged: list[str] = []
    blob = path.name.lower()
    tagged.extend(re.findall(r"(?:^|[_\-.])([a-z]{2,3})(?=[_\-.]|\.[a-z]{3,4}$)", blob))
    tagged.extend(re.findall(r"\(([a-z]{2,3})\)", blob))
    for parent in path.parents:
        name = parent.name.lower().strip()
        if re.fullmatch(r"[a-z]{2,3}", name) or name in LANGUAGE_NAMES or name in NAME_TO_CODE:
            tagged.append(NAME_TO_CODE.get(name, name))
        if name in {"zh-cn", "zh_cn", "zh-tw", "zh_tw", "pt-br", "pt_br"}:
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
    haystack = fold(" ".join(_path_tokens(path)))
    digits = isbn_digits(" ".join(_path_tokens(path)))
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
            elif alias_fold in haystack and len(alias_fold) >= 10:
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
        for path in sorted(folder.rglob("*")):
            if path.suffix.lower() not in {".pdf", ".txt"}:
                continue
            key = str(path).lower()
            if key in seen:
                continue
            seen.add(key)
            files.append(path)
    return files


def select_english_sources(config: dict) -> list[Path]:
    explicit = [Path(item) for item in config.get("english_sources", []) if item]
    folders = [Path(item) for item in config.get("english_dirs", []) if item]
    found = [path for path in collect_pdfs(folders) if not _should_skip(path)]
    ranked: dict[str, Path] = {}
    for path in found:
        language = infer_language(path)
        if language not in {"en", "und"}:
            continue
        if catalog_book_id(path) and language != "en" and not _looks_english(path):
            continue
        if _alias_book_id(path) and not _looks_english(path) and language != "en":
            continue
        book_id = infer_book_id(path)
        if not book_id:
            continue
        current = ranked.get(book_id)
        if current is None or _english_rank(path) > _english_rank(current):
            ranked[book_id] = path
    by_id = {infer_book_id(path): path for path in explicit if path}
    by_id.update(ranked)
    for path in explicit:
        if path:
            by_id[infer_book_id(path)] = path
    return [path for path in by_id.values() if path]


def discover_pairs(config: dict, passwords: list[str] | None = None) -> list[BookPair]:
    english_sources = select_english_sources(config)
    english_by_id = {infer_book_id(path): path for path in english_sources if infer_book_id(path)}
    peek = bool(config.get("peek_language", True))

    translation_folders = [Path(item) for item in config.get("translations_dirs", []) if item]
    if config.get("translations_dir"):
        translation_folders.append(Path(config["translations_dir"]))
    extra = [Path(item) for item in config.get("reference_translations", []) if item]

    candidates = list(extra)
    candidates.extend(collect_pdfs(translation_folders))

    pairs: list[BookPair] = []
    seen: set[tuple[str, str]] = set()
    for translated in candidates:
        if _should_skip(translated):
            continue
        language = infer_language(translated, passwords=passwords, peek=peek)
        if language == "en":
            continue
        book_id = _match_book_id(translated, english_by_id)
        if not book_id:
            continue
        english_path = english_by_id[book_id]
        if _same_file(translated, english_path):
            continue
        if language == "und" and _looks_english(translated):
            continue
        key = (str(english_path.resolve()) if english_path.exists() else str(english_path), str(translated))
        if key in seen:
            continue
        seen.add(key)
        pairs.append(
            BookPair(
                english=english_path,
                translated=translated,
                language=language,
                book_id=book_id,
            )
        )
    pairs.sort(key=lambda item: (item.book_id, item.language, str(item.translated)))
    return pairs


def translation_candidates(config: dict) -> list[Path]:
    translation_folders = [Path(item) for item in config.get("translations_dirs", []) if item]
    if config.get("translations_dir"):
        translation_folders.append(Path(config["translations_dir"]))
    extra = [Path(item) for item in config.get("reference_translations", []) if item]
    files = list(extra)
    files.extend(collect_pdfs(translation_folders))
    return files


def unmatched_translations(config: dict, passwords: list[str] | None = None) -> list[tuple[Path, str]]:
    english_by_id = {
        infer_book_id(path): path
        for path in select_english_sources(config)
        if infer_book_id(path)
    }
    paired = {pair.translated.resolve() if pair.translated.exists() else pair.translated for pair in discover_pairs(config, passwords)}
    leftover: list[tuple[Path, str]] = []
    for path in translation_candidates(config):
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if resolved in paired:
            continue
        leftover.append((path, _skip_reason(path, english_by_id, passwords)))
    return leftover


def inventory_rows(config: dict, passwords: list[str] | None = None) -> list[dict[str, str]]:
    """Describe every PDF the config can see, whether or not it paired."""
    peek = bool(config.get("peek_language", True))
    rows: list[dict[str, str]] = []
    for path in select_english_sources(config):
        rows.append(
            {
                "role": "english",
                "book_id": infer_book_id(path),
                "language": "en",
                "path": str(path),
                "note": "",
            }
        )
    english_by_id = {
        infer_book_id(path): path
        for path in select_english_sources(config)
        if infer_book_id(path)
    }
    paired = {pair.translated.resolve() if pair.translated.exists() else pair.translated for pair in discover_pairs(config, passwords)}
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
            note = _skip_reason(path, english_by_id, passwords)
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


def _skip_reason(path: Path, english_by_id: dict[str, Path], passwords: list[str] | None = None) -> str:
    if _should_skip(path):
        return "skipped DO-NOT-USE/BIODUP"
    language = infer_language(path, passwords=passwords, peek=bool(passwords is not None))
    if language == "en":
        return "looks like English, not a translation"
    if language == "und" and _looks_english(path):
        return "English interior/filename without a language tag"
    if not _match_book_id(path, english_by_id):
        return "no matching English title"
    return "already paired or same file"


def _match_book_id(translated: Path, english_by_id: dict[str, Path]) -> str | None:
    catalog_id = catalog_book_id(translated)
    if catalog_id:
        resolved = _resolve_english_id(catalog_id, english_by_id)
        if resolved:
            return resolved

    translated_id = infer_book_id(translated)
    alias = _alias_book_id(translated)
    if alias:
        for book_id in english_by_id:
            if alias in book_id or book_id in alias or fold(alias) in fold(book_id) or fold(book_id) in fold(alias):
                return book_id
    if translated_id in english_by_id:
        return translated_id

    haystack = fold(" ".join(_path_tokens(translated)))
    best = None
    best_score = 0.0
    for book_id in english_by_id:
        en_tokens = [token for token in fold(book_id).split() if len(token) > 3]
        overlap = sum(1 for token in en_tokens if token in haystack)
        ratio = SequenceMatcher(None, fold(book_id), fold(translated_id)).ratio() if translated_id else 0.0
        score = overlap + ratio
        distinctive = overlap >= 1 and any(len(token) >= 5 for token in en_tokens if token in haystack)
        if distinctive and score > best_score:
            best = book_id
            best_score = score
        elif overlap >= 2 and score > best_score:
            best = book_id
            best_score = score
        elif ratio >= 0.62 and score > best_score:
            best = book_id
            best_score = score
    return best


def _resolve_english_id(book_id: str, english_by_id: dict[str, Path]) -> str | None:
    if book_id in english_by_id:
        return book_id
    book = BOOKS_BY_ID.get(book_id)
    if book and book.fallback and book.fallback in english_by_id:
        return book.fallback
    if book and book.family:
        for other_id, path in english_by_id.items():
            other = BOOKS_BY_ID.get(other_id)
            if other and other.family == book.family:
                return other_id
            if book.family in fold(other_id) or fold(book.title.split(" - ")[0]) in fold(str(path)):
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


def _alias_book_id(path: Path) -> str | None:
    haystack = fold(" ".join(_path_tokens(path)))
    catalog_id = catalog_book_id(path)
    if catalog_id:
        book = BOOKS_BY_ID[catalog_id]
        return fold(book.title)
    for alias, book_id in sorted(SHORT_CODES.items(), key=lambda item: -len(item[0])):
        if re.search(rf"\b{re.escape(alias)}\b", haystack):
            return fold(BOOKS_BY_ID[book_id].title)
    return None


def _path_tokens(path: Path) -> list[str]:
    parts = [path.stem.lower()]
    parts.extend(parent.name.lower() for parent in path.parents if parent.name)
    return parts


def _looks_english(path: Path) -> bool:
    blob = f"{path.stem} {path.parent.name}".lower()
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
    score = 0
    if "complete" in name:
        score += 5
    if "final" in name and "do-not-use" not in name:
        score += 4
    if "2026" in name:
        score += 2
    if "interior" in name:
        score -= 1
    if "v2" in name:
        score -= 1
    return score


def _should_skip(path: Path) -> bool:
    name = path.name.lower()
    return any(marker in name for marker in _SKIP_NAME_MARKERS)


def _same_file(left: Path, right: Path) -> bool:
    try:
        return left.resolve() == right.resolve()
    except OSError:
        return left == right
