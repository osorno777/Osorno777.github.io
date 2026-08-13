from __future__ import annotations

import re
from collections import Counter

from translation_qa.models import Finding, Severity
from translation_qa.segment import extract_scripture_refs

_NUMBER_RE = re.compile(r"\b\d{1,4}(?:[.,]\d+)?\b")
_YEAR_RE = re.compile(r"\b(?:1[6-9]\d{2}|20[0-2]\d)\b")


def check_numbers_and_refs(english: str, translated: str, *, sentence_index: int | None = None) -> list[Finding]:
    findings: list[Finding] = []
    en_nums = _significant_numbers(english)
    tr_nums = _significant_numbers(translated)
    missing = en_nums - tr_nums
    extra = tr_nums - en_nums
    if missing:
        findings.append(
            Finding(
                check="numbers.missing",
                severity=Severity.DEFECT,
                message=f"Source numbers missing from the translation: {', '.join(sorted(missing))}",
                english=english,
                translated=translated,
                sentence_index=sentence_index,
            )
        )
    if extra and not missing:
        findings.append(
            Finding(
                check="numbers.extra",
                severity=Severity.WARNING,
                message=f"Translation introduces numbers not in the source: {', '.join(sorted(extra))}",
                english=english,
                translated=translated,
                sentence_index=sentence_index,
            )
        )

    en_refs = {_norm_ref(item) for item in extract_scripture_refs(english)}
    tr_refs = {_norm_ref(item) for item in extract_scripture_refs(translated)}
    lost_refs = en_refs - tr_refs
    if lost_refs:
        findings.append(
            Finding(
                check="numbers.scripture_missing",
                severity=Severity.DEFECT,
                message=f"Scripture or citation references dropped: {', '.join(sorted(lost_refs))}",
                english=english,
                translated=translated,
                sentence_index=sentence_index,
            )
        )
    return findings


def _significant_numbers(text: str) -> Counter[str]:
    values: list[str] = []
    for match in _NUMBER_RE.finditer(text):
        raw = match.group(0)
        if len(raw) == 1:
            continue
        values.append(raw.replace(",", "").replace(".", ""))
    for match in _YEAR_RE.finditer(text):
        values.append(match.group(0))
    return Counter(values)


def _norm_ref(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip().lower()
    value = value.replace(".", "")
    return value
