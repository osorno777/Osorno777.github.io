from __future__ import annotations

import re

from translation_qa.models import Finding, Severity
from translation_qa.segment import ENGLISH_STOPWORDS

_ENGLISH_RUN = re.compile(
    r"\b([A-Za-z][A-Za-z']+(?:\s+[A-Za-z][A-Za-z']+){3,})\b"
)

# Words that commonly survive in a legitimate translation (names, places, brands).
_ALLOW_SINGLE = {
    "jesus", "christ", "god", "bible", "israel", "jerusalem", "rome", "paul",
    "peter", "john", "matthew", "mark", "luke", "moses", "abraham", "david",
    "kdp", "amazon", "ingramspark", "publishdrive", "streetlib", "kindle",
}


def check_residual_english(text: str, language: str, *, sentence_index: int | None = None) -> list[Finding]:
    if language in {"en", "und"}:
        return []
    findings: list[Finding] = []
    for match in _ENGLISH_RUN.finditer(text):
        run = match.group(1)
        words = [part.lower() for part in re.findall(r"[A-Za-z']+", run)]
        content = [word for word in words if word not in ENGLISH_STOPWORDS and word not in _ALLOW_SINGLE]
        if len(content) < 2:
            continue
        # Latin-script languages can include English loanwords; require a function-word spine.
        function_hits = sum(1 for word in words if word in ENGLISH_STOPWORDS)
        if function_hits < 2:
            continue
        findings.append(
            Finding(
                check="residual_english.run",
                severity=Severity.DEFECT,
                message="Untranslated English sentence fragment in the target text.",
                translated=run,
                sentence_index=sentence_index,
                extra={"language": language},
            )
        )
    return findings
