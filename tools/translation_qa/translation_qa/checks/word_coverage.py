from __future__ import annotations

import re
from difflib import SequenceMatcher

from translation_qa.models import Finding, Severity
from translation_qa.segment import Token, content_words

_PROPER_RE = re.compile(r"^[A-ZÁÉÍÓÚÜÑÀÈÌÒÙÄÖÅÆØÇ][A-Za-zÁÉÍÓÚÜÑÀÈÌÒÙÄÖÅÆØÇ'’-]+$")


def check_word_coverage(english: str, translated: str, *, sentence_index: int | None = None) -> list[Finding]:
    """Deterministic word-level pass: numbers, names, and dropped-clause heuristics."""
    findings: list[Finding] = []
    words = content_words(english)
    if not english.strip():
        if translated.strip():
            findings.append(
                Finding(
                    check="word.addition",
                    severity=Severity.WARNING,
                    message="Translation has text with no aligned English sentence.",
                    translated=translated,
                    sentence_index=sentence_index,
                )
            )
        return findings
    if not translated.strip():
        findings.append(
            Finding(
                check="word.omission",
                severity=Severity.DEFECT,
                message="English sentence has no aligned translation.",
                english=english,
                sentence_index=sentence_index,
            )
        )
        return findings

    tr_fold = _fold(translated)
    for token in words:
        status = _present(token, translated, tr_fold)
        if status == "present":
            continue
        if token.kind in {"number", "scripture"} or _is_proper(token, english):
            findings.append(
                Finding(
                    check=f"word.missing_{token.kind if token.kind != 'word' else 'name'}",
                    severity=Severity.DEFECT,
                    message=f"Source token {token.text!r} was not found in the translation.",
                    english=english,
                    translated=translated,
                    word=token.text,
                    sentence_index=sentence_index,
                )
            )

    en_len = max(len(english), 1)
    ratio = len(translated) / en_len
    if ratio < 0.45 and len(words) >= 6:
        findings.append(
            Finding(
                check="word.possible_omission",
                severity=Severity.WARNING,
                message=f"Translation is only {ratio:.0%} as long as the English sentence; clauses may have been dropped.",
                english=english,
                translated=translated,
                sentence_index=sentence_index,
            )
        )
    elif ratio > 2.2 and len(words) >= 4:
        findings.append(
            Finding(
                check="word.possible_addition",
                severity=Severity.WARNING,
                message=f"Translation is {ratio:.0%} the length of the English sentence; commentary may have been added.",
                english=english,
                translated=translated,
                sentence_index=sentence_index,
            )
        )
    return findings


def _present(token: Token, translated: str, tr_fold: str) -> str:
    raw = token.text
    if token.kind == "number":
        digits = raw.replace(",", "").replace(".", "")
        if digits and digits in translated.replace(",", "").replace(".", ""):
            return "present"
        return "missing"
    if token.kind == "scripture":
        compact = re.sub(r"\s+", "", raw.lower())
        if compact in re.sub(r"\s+", "", translated.lower()):
            return "present"
        # Chapter:verse often survives even when the book name is localized.
        verse = re.search(r"\d+:\d+", raw)
        if verse and verse.group(0) in translated:
            return "present"
        return "missing"

    folded = _fold(raw)
    if folded and folded in tr_fold:
        return "present"
    if _fuzzy_name(raw, translated):
        return "present"
    return "missing"


def _is_proper(token: Token, sentence: str) -> bool:
    if not _PROPER_RE.match(token.text):
        return False
    return token.start > 0 and sentence[token.start - 1] not in {".", "!", "?", "\n"}


def _fuzzy_name(name: str, translated: str) -> bool:
    if len(name) < 4:
        return False
    candidates = re.findall(r"[A-Za-zÁ-ÿ?-ž?-?]{3,}", translated)
    for candidate in candidates:
        if SequenceMatcher(None, name.lower(), candidate.lower()).ratio() >= 0.78:
            return True
    return False


def _fold(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())
