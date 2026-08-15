from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    DEFECT = "defect"
    REFUSAL = "refusal"
    CRITICAL = "critical"


@dataclass(frozen=True)
class Finding:
    check: str
    severity: Severity
    message: str
    english: str = ""
    translated: str = ""
    word: str = ""
    sentence_index: int | None = None
    page: int | None = None
    extra: dict[str, str] = field(default_factory=dict)


@dataclass
class Document:
    path: Path
    text: str
    pages: list[str]
    language: str = "und"
    title: str = ""
    encrypted: bool = False
    password_used: bool = False


@dataclass
class AlignedPair:
    index: int
    english: str
    translated: str
    en_start: int
    en_end: int
    tr_start: int
    tr_end: int


@dataclass
class AuditResult:
    english_path: str
    translated_path: str
    language: str
    findings: list[Finding]
    sentences_compared: int
    words_checked: int
    words_unverified: int
    english_pages: int
    translated_pages: int

    @property
    def counts(self) -> dict[str, int]:
        tallies = {item.value: 0 for item in Severity}
        for finding in self.findings:
            tallies[finding.severity.value] += 1
        return tallies
