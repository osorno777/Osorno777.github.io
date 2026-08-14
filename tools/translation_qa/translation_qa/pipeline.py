from __future__ import annotations

from pathlib import Path

from translation_qa.align import align_sentences
from translation_qa.checks.llm_judge import JudgeError, judge_available, judge_pair
from translation_qa.checks.numbers import check_numbers_and_refs
from translation_qa.checks.refusals import check_refusals
from translation_qa.checks.residual_english import check_residual_english
from translation_qa.checks.structure import check_structure
from translation_qa.checks.word_coverage import check_word_coverage
from translation_qa.extract import extract_epub, extract_pdf, extract_plain
from translation_qa.models import AuditResult, Document, Finding, Severity
from translation_qa.passwords import load_pdf_passwords
from translation_qa.segment import content_words


def load_document(path: Path, language: str, passwords: list[str] | None = None) -> Document:
    if path.suffix.lower() == ".pdf":
        document = extract_pdf(path, passwords=passwords)
    elif path.suffix.lower() == ".epub":
        document = extract_epub(path, language=language)
    else:
        document = extract_plain(path, language=language)
    document.language = language
    return document


def audit_texts(
    english: str,
    translated: str,
    language: str,
    *,
    word_by_word: bool = True,
    use_llm: bool = False,
    delay_seconds: float = 0.0,
    max_sentences: int | None = None,
    english_doc: Document | None = None,
    translated_doc: Document | None = None,
) -> AuditResult:
    findings: list[Finding] = []
    findings.extend(check_refusals(translated))
    findings.extend(check_residual_english(translated, language))

    if english_doc and translated_doc:
        findings.extend(check_structure(english_doc, translated_doc))

    pairs = align_sentences(english, translated)
    if max_sentences is not None:
        pairs = pairs[: max(0, max_sentences)]

    words_checked = 0
    words_unverified = 0
    for pair in pairs:
        if not pair.english and not pair.translated:
            continue
        findings.extend(check_numbers_and_refs(pair.english, pair.translated, sentence_index=pair.index))
        findings.extend(check_residual_english(pair.translated, language, sentence_index=pair.index))
        findings.extend(check_refusals(pair.translated, sentence_index=pair.index))
        if word_by_word:
            words = content_words(pair.english)
            words_checked += len(words)
            local = check_word_coverage(pair.english, pair.translated, sentence_index=pair.index)
            findings.extend(local)
            if use_llm and judge_available():
                try:
                    findings.extend(
                        judge_pair(
                            pair.english,
                            pair.translated,
                            language,
                            sentence_index=pair.index,
                            delay_seconds=delay_seconds,
                        )
                    )
                except JudgeError as exc:
                    findings.append(
                        Finding(
                            check="llm.error",
                            severity=Severity.WARNING,
                            message=str(exc),
                            sentence_index=pair.index,
                        )
                    )
                    words_unverified += len(words)
            else:
                verified = {item.word for item in local if item.word}
                words_unverified += sum(1 for token in words if token.text not in verified)

    return AuditResult(
        english_path=str(english_doc.path) if english_doc else "",
        translated_path=str(translated_doc.path) if translated_doc else "",
        language=language,
        findings=_dedupe(findings),
        sentences_compared=len(pairs),
        words_checked=words_checked,
        words_unverified=words_unverified,
        english_pages=len(english_doc.pages) if english_doc else 0,
        translated_pages=len(translated_doc.pages) if translated_doc else 0,
    )


def audit_files(
    english_path: Path,
    translated_path: Path,
    language: str,
    *,
    word_by_word: bool = True,
    use_llm: bool = False,
    delay_seconds: float = 0.0,
    max_sentences: int | None = None,
    passwords: list[str] | None = None,
) -> AuditResult:
    passwords = passwords if passwords is not None else load_pdf_passwords()
    english_doc = load_document(english_path, "en", passwords)
    translated_doc = load_document(translated_path, language, passwords)
    return audit_texts(
        english_doc.text,
        translated_doc.text,
        language,
        word_by_word=word_by_word,
        use_llm=use_llm,
        delay_seconds=delay_seconds,
        max_sentences=max_sentences,
        english_doc=english_doc,
        translated_doc=translated_doc,
    )


def _dedupe(findings: list[Finding]) -> list[Finding]:
    seen: set[tuple[str, str, str, int | None]] = set()
    unique: list[Finding] = []
    for finding in findings:
        key = (finding.check, finding.message, finding.word, finding.sentence_index)
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)
    return unique
