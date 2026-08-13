from __future__ import annotations

import re

from translation_qa.models import Finding, Severity

# Patterns that show up when a model refuses, hedges, or narrates instead of translating.
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("ai_self_id", re.compile(r"\b(as an ai|as an artificial intelligence|i am an ai|soy una? (ia|inteligencia artificial)|como inteligencia artificial|??????|??????)\b", re.I)),
    ("cannot_assist", re.compile(r"\b(i (can'?t|cannot|am unable to|won'?t be able to) (help|assist|provide|translate|continue|generate|comply)|no puedo (ayudar|traducir|continuar|proporcionar)|??[?,]????|???(??|??|??))\b", re.I)),
    ("policy_block", re.compile(r"\b(against my (guidelines|policies)|content policy|usage policy|i must decline|i (have to|must) refuse|??.{0,12}??|???.{0,12}??)\b", re.I)),
    ("meta_translation", re.compile(r"\b(here is (the|a) translation|sure[,.]? i('ll| will) translate|the following is (a |the )?translation|a continuaci[oó]n (est[aá]|va) la traducci[oó]n|?????)\b", re.I)),
    ("partial_stop", re.compile(r"\b(i('ll| will) stop (here|at this point)|translation (stops|ends) here|unable to (finish|complete) the translation)\b", re.I)),
    ("copyright_block", re.compile(r"\b(i (can'?t|cannot) (reproduce|provide copyrighted)|due to copyright)\b", re.I)),
    ("placeholder", re.compile(r"\[(?:refusal|redacted|omitted|unable to translate|todo|tbd|insert translation)\]", re.I)),
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
