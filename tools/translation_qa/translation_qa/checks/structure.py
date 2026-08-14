from __future__ import annotations

import re

from translation_qa.models import Document, Finding, Severity

_CHAPTER_RE = re.compile(
    r"(?im)^\s*(chapter|cap[i\u00ed]tulo|chapitre|kapitel|"
    r"rozdzia\u0142|\u0433\u043b\u0430\u0432\u0430|\u7ae0)\s+"
    r"([0-9ivxlcdm]+|[\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e]+)\b"
)


def check_structure(english: Document, translated: Document) -> list[Finding]:
    findings: list[Finding] = []
    en_pages = max(len([page for page in english.pages if page.strip()]), 1)
    tr_pages = max(len([page for page in translated.pages if page.strip()]), 1)
    page_ratio = tr_pages / en_pages
    if page_ratio < 0.55:
        findings.append(
            Finding(
                check="structure.short_book",
                severity=Severity.CRITICAL,
                message=(
                    f"Translated PDF is much shorter than the English source "
                    f"({tr_pages} vs {en_pages} text pages). Likely truncation or refusal mid-book."
                ),
            )
        )
    elif page_ratio < 0.75:
        findings.append(
            Finding(
                check="structure.short_book",
                severity=Severity.DEFECT,
                message=f"Translated PDF is shorter than expected ({tr_pages} vs {en_pages} text pages).",
            )
        )

    en_len = max(len(english.text), 1)
    tr_len = len(translated.text)
    char_ratio = tr_len / en_len
    if char_ratio < 0.45:
        findings.append(
            Finding(
                check="structure.short_text",
                severity=Severity.CRITICAL,
                message=f"Extracted translation text is only {char_ratio:.0%} of the English length.",
            )
        )

    en_chapters = _CHAPTER_RE.findall(english.text)
    tr_chapters = _CHAPTER_RE.findall(translated.text)
    if en_chapters and len(tr_chapters) + 1 < len(en_chapters):
        findings.append(
            Finding(
                check="structure.missing_chapters",
                severity=Severity.DEFECT,
                message=f"English has {len(en_chapters)} chapter headings; translation has {len(tr_chapters)}.",
            )
        )

    replacement = translated.text.count("\ufffd") + translated.text.count("?")
    if translated.text and replacement / max(len(translated.text), 1) > 0.02 and translated.text.count("\ufffd") > 10:
        findings.append(
            Finding(
                check="structure.garbled",
                severity=Severity.DEFECT,
                message="High density of replacement characters; encoding or extraction is damaged.",
            )
        )
    return findings
