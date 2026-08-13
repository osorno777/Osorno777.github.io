from __future__ import annotations

import re

from translation_qa.models import Finding, Severity

# Patterns that show up when a model refuses, hedges, or narrates instead of translating.
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "ai_self_id",
        re.compile(
            r"\b(as an ai|as an artificial intelligence|i am an ai|"
            r"soy una? (ia|inteligencia artificial)|como inteligencia artificial|"
            r"\u4f5c\u4e3a\u4eba\u5de5\u667a\u80fd|\u6211\u662f\u4eba\u5de5\u667a\u80fd)\b",
            re.I,
        ),
    ),
    (
        "cannot_assist",
        re.compile(
            r"\b(i (can'?t|cannot|am unable to|won'?t be able to) "
            r"(help|assist|provide|translate|continue|generate|comply)|"
            r"no puedo (ayudar|traducir|continuar|proporcionar)|"
            r"\u62b1\u6b49[,\uff0c]?\u6211\u65e0\u6cd5|"
            r"\u6211\u4e0d\u80fd(\u5e2e\u52a9|\u7ffb\u8bd1|\u7ee7\u7eed))\b",
            re.I,
        ),
    ),
    (
        "policy_block",
        re.compile(
            r"\b(against my (guidelines|policies)|content policy|usage policy|"
            r"i must decline|i (have to|must) refuse|"
            r"\u8fdd\u53cd.{0,12}\u653f\u7b56|\u4e0d\u7b26\u5408.{0,12}\u89c4\u5b9a)\b",
            re.I,
        ),
    ),
    (
        "meta_translation",
        re.compile(
            r"\b(here is (the|a) translation|sure[,.]? i('ll| will) translate|"
            r"the following is (a |the )?translation|"
            r"a continuaci[o\u00f3]n (est[a\u00e1]|va) la traducci[o\u00f3]n|"
            r"\u4ee5\u4e0b\u662f\u7ffb\u8bd1)\b",
            re.I,
        ),
    ),
    (
        "partial_stop",
        re.compile(
            r"\b(i('ll| will) stop (here|at this point)|"
            r"translation (stops|ends) here|"
            r"unable to (finish|complete) the translation)\b",
            re.I,
        ),
    ),
    (
        "copyright_block",
        re.compile(
            r"\b(i (can'?t|cannot) (reproduce|provide copyrighted)|due to copyright)\b",
            re.I,
        ),
    ),
    (
        "placeholder",
        re.compile(
            r"\[(?:refusal|redacted|omitted|unable to translate|todo|tbd|insert translation)\]",
            re.I,
        ),
    ),
]


def check_refusals(text: str, *, sentence_index: int | None = None) -> list[Finding]:
    findings: list[Finding] = []
    for name, pattern in _PATTERNS:
        for match in pattern.finditer(text):
            snippet = _snippet(text, match.start(), match.end())
            severity = Severity.REFUSAL if name != "meta_translation" else Severity.DEFECT
            findings.append(
                Finding(
                    check=f"refusal.{name}",
                    severity=severity,
                    message=f"Possible model refusal or leftover prompt residue: {match.group(0)!r}",
                    translated=snippet,
                    sentence_index=sentence_index,
                )
            )
    findings.extend(_repeated_boilerplate(text, sentence_index))
    return findings


def _repeated_boilerplate(text: str, sentence_index: int | None) -> list[Finding]:
    lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 40]
    if len(lines) < 6:
        return []
    counts: dict[str, int] = {}
    for line in lines:
        counts[line] = counts.get(line, 0) + 1
    findings: list[Finding] = []
    for line, count in counts.items():
        if count >= 4:
            findings.append(
                Finding(
                    check="refusal.repeated_boilerplate",
                    severity=Severity.DEFECT,
                    message=f"The same long line repeats {count} times; likely a paste/generation defect.",
                    translated=line[:240],
                    sentence_index=sentence_index,
                )
            )
    return findings


def _snippet(text: str, start: int, end: int, radius: int = 80) -> str:
    lo = max(0, start - radius)
    hi = min(len(text), end + radius)
    return text[lo:hi].replace("\n", " ").strip()
