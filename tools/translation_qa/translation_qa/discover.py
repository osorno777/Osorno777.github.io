from __future__ import annotations

import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from translation_qa.languages import LANGUAGE_NAMES, NAME_TO_CODE

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

# Short codes and translated titles that should map to an English book id.
BOOK_ALIASES: dict[str, str] = {
    "btc": "bearing the cross",
    "btw": "behind the walls",
    "su": "suffering unjustly",
    "padeciendo": "suffering unjustly",
    "padeciendo injustamente": "suffering unjustly",
    "detras de los muros": "behind the walls",
    "detras de las paredes": "behind the walls",
    "llevando la cruz": "bearing the cross",
    "primer": "primer on modern themes",
    "allodial": "building regulation market alternatives",
    "ctpp": "christian theology of public policy",
    "bible and government": "bible and government",
    "pro life": "pro life policy",
    "life in chile": "life in chile",
}


@dataclass(frozen=True)
class BookPair:
    english: Path
    translated: Path
    language: str
    book_id: str


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def infer_language(path: Path) -> str:
    haystack = " ".join(_path_tokens(path))
    parts = re.split(r"[ .()\[\]_/-]+", haystack)
    for part in parts:
        if part in LANGUAGE_NAMES and part != "en":
            return part
        if part in {"zh-cn", "zh_cn", "cn"}:
            return "zh"
        if part in {"zh-tw", "zh_tw", "tw"}:
            return "zh-tw"
        if part in {"pt-br", "pt_br", "br"}:
            return "pt-br"
    for name, code in sorted(NAME_TO_CODE.items(), key=lambda item: -len(item[0])):
        if name == "english":
            continue
        if re.search(rf"\b{re.escape(name)}\b", haystack):
            return code
    if _looks_english(path):
        return "en"
    return "und"


def infer_book_id(path: Path) -> str:
    stem = path.stem.lower()
    stem = re.sub(r"\((complete|2026|en|english|interior|final|v\d+)\)", " ", stem, flags=re.I)
    stem = re.sub(r"\b(complete|english|en|interior|final|biodup|v\d+|pp|\d+pp)\b", " ", stem, flags=re.I)
    stem = re.sub(r"[^a-z0-9]+", " ", stem).strip()
    tokens = [token for token in stem.split() if token not in LANGUAGE_NAMES and len(token) > 1]
    return " ".join(tokens[:8])


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
        if infer_language(path) not in {"en", "und"}:
            continue
        if _alias_book_id(path) and not _looks_english(path):
            continue
        book_id = infer_book_id(path)
        if not book_id:
            continue
        current = ranked.get(book_id)
        if current is None or _english_rank(path) > _english_rank(current):
            ranked[book_id] = path
    by_id = {infer_book_id(path): path for path in explicit if path}
    by_id.update(ranked)
    # Explicit paths win when they exist.
    for path in explicit:
        if path:
            by_id[infer_book_id(path)] = path
    return [path for path in by_id.values() if path]


def discover_pairs(config: dict) -> list[BookPair]:
    english_sources = select_english_sources(config)
    english_by_id = {infer_book_id(path): path for path in english_sources if infer_book_id(path)}

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
        language = infer_language(translated)
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


def unmatched_translations(config: dict) -> list[tuple[Path, str]]:
    english_by_id = {
        infer_book_id(path): path
        for path in select_english_sources(config)
        if infer_book_id(path)
    }
    paired = {pair.translated.resolve() if pair.translated.exists() else pair.translated for pair in discover_pairs(config)}
    leftover: list[tuple[Path, str]] = []
    for path in translation_candidates(config):
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if resolved in paired:
            continue
        leftover.append((path, _skip_reason(path, english_by_id)))
    return leftover


def _skip_reason(path: Path, english_by_id: dict[str, Path]) -> str:
    if _should_skip(path):
        return "skipped DO-NOT-USE/BIODUP"
    language = infer_language(path)
    if language == "en":
        return "looks like English, not a translation"
    if language == "und" and _looks_english(path):
        return "English interior/filename without a language tag"
    if not _match_book_id(path, english_by_id):
        return "no matching English title"
    return "already paired or same file"



def _match_book_id(translated: Path, english_by_id: dict[str, Path]) -> str | None:
    translated_id = infer_book_id(translated)
    alias = _alias_book_id(translated)
    if alias:
        for book_id in english_by_id:
            if alias in book_id or book_id in alias:
                return book_id
    if translated_id in english_by_id:
        return translated_id

    haystack = " ".join(_path_tokens(translated))
    best = None
    best_score = 0.0
    for book_id in english_by_id:
        en_tokens = [token for token in book_id.split() if len(token) > 3]
        overlap = sum(1 for token in en_tokens if token in haystack)
        ratio = SequenceMatcher(None, book_id, translated_id).ratio() if translated_id else 0.0
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


def _alias_book_id(path: Path) -> str | None:
    haystack = " ".join(_path_tokens(path))
    for alias, book_id in sorted(BOOK_ALIASES.items(), key=lambda item: -len(item[0])):
        if re.search(rf"\b{re.escape(alias)}\b", haystack):
            return book_id
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
        "future", "surviving", "chilean", "justice", "defending",
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
