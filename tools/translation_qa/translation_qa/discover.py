from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from translation_qa.languages import LANGUAGE_NAMES, NAME_TO_CODE


@dataclass(frozen=True)
class BookPair:
    english: Path
    translated: Path
    language: str
    book_id: str


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def infer_language(path: Path) -> str:
    stem = path.stem.lower().replace("_", " ").replace("-", " ")
    parts = re.split(r"[ .()\[\]]+", stem)
    for part in parts:
        if part in LANGUAGE_NAMES:
            return part
    for name, code in sorted(NAME_TO_CODE.items(), key=lambda item: -len(item[0])):
        if re.search(rf"\b{re.escape(name)}\b", stem):
            return code
    parent = path.parent.name.lower()
    if parent in LANGUAGE_NAMES:
        return parent
    if parent in NAME_TO_CODE:
        return NAME_TO_CODE[parent]
    return "und"


def infer_book_id(path: Path) -> str:
    stem = path.stem.lower()
    stem = re.sub(r"\((complete|2026|en|english)\)", "", stem, flags=re.I)
    stem = re.sub(r"\b(complete|english|en)\b", "", stem, flags=re.I)
    stem = re.sub(r"[^a-z0-9]+", " ", stem).strip()
    return " ".join(stem.split()[:6])


def discover_pairs(config: dict) -> list[BookPair]:
    pairs: list[BookPair] = []
    english_sources = [Path(item) for item in config.get("english_sources", [])]
    translations_dir = Path(config["translations_dir"]) if config.get("translations_dir") else None
    extra = [Path(item) for item in config.get("reference_translations", [])]

    english_by_id = {infer_book_id(path): path for path in english_sources if path}

    candidates: list[Path] = list(extra)
    if translations_dir and translations_dir.is_dir():
        candidates.extend(sorted(translations_dir.rglob("*.pdf")))
        candidates.extend(sorted(translations_dir.rglob("*.txt")))

    seen: set[tuple[str, str]] = set()
    for translated in candidates:
        language = infer_language(translated)
        if language == "en":
            continue
        book_id = _match_book_id(translated, english_by_id)
        if not book_id:
            continue
        english_path = english_by_id[book_id]
        try:
            same_file = translated.resolve() == english_path.resolve()
        except OSError:
            same_file = translated == english_path
        if same_file:
            continue
        key = (str(english_path), str(translated))
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
    return pairs


def _match_book_id(translated: Path, english_by_id: dict[str, Path]) -> str | None:
    translated_id = infer_book_id(translated)
    if translated_id in english_by_id:
        return translated_id
    tr_tokens = set(translated_id.split())
    best = None
    best_score = 0
    for book_id in english_by_id:
        en_tokens = set(book_id.split())
        score = len(en_tokens & tr_tokens)
        if score > best_score and score >= 2:
            best = book_id
            best_score = score
    return best
