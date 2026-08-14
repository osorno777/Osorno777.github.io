from __future__ import annotations

import csv
import errno
import json
from collections import Counter
from html import escape
from pathlib import Path

from translation_qa.models import AuditResult, Finding, Severity

DEFECT_HTML_EXAMPLES = 150
DEFECT_JSON_EXAMPLES = 50
SNIPPET_LEN = 280
PRIORITY = {Severity.CRITICAL, Severity.REFUSAL, Severity.WARNING}


class DiskFullError(OSError):
    """Raised when a report file cannot be written because the disk is full."""

    def __init__(self, path: Path, html_written: bool) -> None:
        super().__init__(errno.ENOSPC, "No space left on device", str(path))
        self.path = path
        self.html_written = html_written


def is_disk_full(exc: BaseException) -> bool:
    if not isinstance(exc, OSError):
        return False
    if getattr(exc, "errno", None) in {errno.ENOSPC, 28}:
        return True
    text = str(exc).lower()
    return "no space left" in text or "not enough space" in text or "disk full" in text


def write_reports(
    result: AuditResult,
    output_dir: Path,
    stem: str,
    *,
    full: bool = False,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / f"{stem}.html"
    json_path = output_dir / f"{stem}.json"
    csv_path = output_dir / f"{stem}.csv"
    written: dict[str, Path] = {}
    html_ok = False
    try:
        html_path.write_text(_render_html(result, full=full), encoding="utf-8")
        html_ok = True
        written["html"] = html_path
        json_path.write_text(
            json.dumps(_as_dict(result, full=full), ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        written["json"] = json_path
        if full:
            _write_csv(csv_path, result.findings)
            written["csv"] = csv_path
        elif csv_path.exists():
            csv_path.unlink()
    except OSError as exc:
        if is_disk_full(exc):
            raise DiskFullError(html_path if not html_ok else json_path, html_ok) from exc
        raise
    return written


def compact_existing_reports(output_dir: Path) -> dict[str, int]:
    """Delete bulky JSON/CSV copies and shrink oversized HTML tables. HTML summaries stay."""
    output_dir.mkdir(parents=True, exist_ok=True)
    deleted_json = 0
    deleted_csv = 0
    shrunk_html = 0
    for path in output_dir.glob("*.json"):
        path.unlink()
        deleted_json += 1
    for path in output_dir.glob("*.csv"):
        path.unlink()
        deleted_csv += 1
    for html_path in output_dir.glob("*.html"):
        try:
            if html_path.stat().st_size < 80_000:
                continue
            original = html_path.read_text(encoding="utf-8")
            compact = _shrink_existing_html(original)
            if compact != original and len(compact) < len(original):
                tmp = html_path.with_suffix(".html.tmp")
                tmp.write_text(compact, encoding="utf-8")
                tmp.replace(html_path)
                shrunk_html += 1
        except OSError:
            continue
    return {"deleted_json": deleted_json, "deleted_csv": deleted_csv, "shrunk_html": shrunk_html}


def _as_dict(result: AuditResult, *, full: bool = False) -> dict:
    payload = {
        "english_path": result.english_path,
        "translated_path": result.translated_path,
        "language": result.language,
        "sentences_compared": result.sentences_compared,
        "words_checked": result.words_checked,
        "words_unverified": result.words_unverified,
        "english_pages": result.english_pages,
        "translated_pages": result.translated_pages,
        "counts": result.counts,
        "defect_checks": _defect_check_counts(result.findings),
    }
    if full:
        payload["findings"] = [_finding_dict(item, snippet=None) for item in result.findings]
        return payload
    priority = [item for item in result.findings if item.severity in PRIORITY]
    defects = [item for item in result.findings if item.severity == Severity.DEFECT]
    payload["priority_findings"] = [_finding_dict(item) for item in priority]
    payload["defect_examples"] = [_finding_dict(item) for item in defects[:DEFECT_JSON_EXAMPLES]]
    return payload


def _finding_dict(item: Finding, snippet: int | None = SNIPPET_LEN) -> dict:
    english = item.english if snippet is None else item.english[:snippet]
    translated = item.translated if snippet is None else item.translated[:snippet]
    return {
        "check": item.check,
        "severity": item.severity.value,
        "message": item.message,
        "word": item.word,
        "sentence_index": item.sentence_index,
        "english": english,
        "translated": translated,
        "extra": item.extra,
    }


def _defect_check_counts(findings: list[Finding]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in findings:
        if item.severity == Severity.DEFECT:
            counts[item.check] += 1
    return dict(counts.most_common())


def _write_csv(path: Path, findings: list[Finding]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["severity", "check", "word", "sentence_index", "message", "english", "translated"],
        )
        writer.writeheader()
        for item in findings:
            writer.writerow(
                {
                    "severity": item.severity.value,
                    "check": item.check,
                    "word": item.word,
                    "sentence_index": item.sentence_index if item.sentence_index is not None else "",
                    "message": item.message,
                    "english": item.english,
                    "translated": item.translated,
                }
            )


def _render_html(result: AuditResult, *, full: bool = False) -> str:
    counts = result.counts
    priority = [item for item in result.findings if item.severity in PRIORITY]
    defects = [item for item in result.findings if item.severity == Severity.DEFECT]
    other = [item for item in result.findings if item.severity not in PRIORITY and item.severity != Severity.DEFECT]
    shown_defects = defects if full else defects[:DEFECT_HTML_EXAMPLES]
    shown_other = other if full else other[:50]
    defect_note = ""
    if not full and len(defects) > DEFECT_HTML_EXAMPLES:
        defect_note = (
            f"<p>Showing {DEFECT_HTML_EXAMPLES} of {len(defects)} defect examples. "
            "Counts by check are in the table below. Re-run with --full-reports for every row.</p>"
        )
    sections = [
        _summary_block(result, counts),
        _check_count_table(_defect_check_counts(result.findings), "Defects by check"),
        _findings_table("Critical, refusals, and warnings", priority),
        defect_note,
        _findings_table("Defect examples", shown_defects),
    ]
    if shown_other:
        sections.append(_findings_table("Other findings", shown_other))
    return (
        "<!DOCTYPE html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n"
        f"<title>Translation QA {escape(result.language)}</title>\n"
        "<style>\n"
        "body { font-family: Georgia, serif; margin: 2rem; }\n"
        "table { border-collapse: collapse; width: 100%; font-size: 0.92rem; }\n"
        "th, td { border: 1px solid #ccc; padding: 0.4rem 0.5rem; vertical-align: top; }\n"
        "th { background: #222; color: #fff; }\n"
        "tr:nth-child(even) { background: #f6f6f6; }\n"
        ".summary span { margin-right: 1rem; }\n"
        "h2 { margin-top: 1.6rem; }\n"
        "</style></head><body>\n"
        + "\n".join(part for part in sections if part)
        + "\n</body></html>\n"
    )


def _summary_block(result: AuditResult, counts: dict[str, int]) -> str:
    return f"""<h1>Translation veracity report</h1>
<p class="summary">
<span>Language: {escape(result.language)}</span>
<span>Sentences: {result.sentences_compared}</span>
<span>Words checked: {result.words_checked}</span>
<span>Unverified without LLM: {result.words_unverified}</span>
<span>Critical: {counts.get('critical', 0)}</span>
<span>Refusals: {counts.get('refusal', 0)}</span>
<span>Defects: {counts.get('defect', 0)}</span>
<span>Warnings: {counts.get('warning', 0)}</span>
</p>
<p>English: {escape(result.english_path)}<br>Translation: {escape(result.translated_path)}</p>"""


def _check_count_table(counts: dict[str, int], heading: str) -> str:
    if not counts:
        return ""
    rows = "".join(
        f"<tr><td>{escape(check)}</td><td>{n}</td></tr>" for check, n in counts.items()
    )
    return (
        f"<h2>{escape(heading)}</h2>\n"
        "<table><thead><tr><th>Check</th><th>Count</th></tr></thead>"
        f"<tbody>\n{rows}\n</tbody></table>"
    )


def _findings_table(heading: str, findings: list[Finding]) -> str:
    if not findings:
        return f"<h2>{escape(heading)}</h2>\n<p>None.</p>"
    rows = []
    for item in findings:
        rows.append(
            "<tr>"
            f"<td>{escape(item.severity.value)}</td>"
            f"<td>{escape(item.check)}</td>"
            f"<td>{escape(item.word)}</td>"
            f"<td>{item.sentence_index if item.sentence_index is not None else ''}</td>"
            f"<td>{escape(item.message)}</td>"
            f"<td>{escape(item.english[:SNIPPET_LEN])}</td>"
            f"<td>{escape(item.translated[:SNIPPET_LEN])}</td>"
            "</tr>"
        )
    body = "\n".join(rows)
    return (
        f"<h2>{escape(heading)}</h2>\n"
        "<table>\n"
        "<thead><tr><th>Severity</th><th>Check</th><th>Word</th><th>#</th>"
        "<th>Message</th><th>English</th><th>Translation</th></tr></thead>\n"
        f"<tbody>\n{body}\n</tbody></table>"
    )


def _shrink_existing_html(text: str) -> str:
    """Keep the summary and a bounded number of table rows in already-written reports."""
    if "<tbody>" not in text:
        return text
    chunks = text.split("<tbody>")
    rebuilt = [chunks[0]]
    total_rows = 0
    total_kept = 0
    defect_kept = 0
    for chunk in chunks[1:]:
        rebuilt.append("<tbody>")
        if "</tbody>" not in chunk:
            rebuilt.append(chunk)
            continue
        body, suffix = chunk.split("</tbody>", 1)
        rows = [row.strip() for row in body.split("</tr>") if "<td>" in row]
        total_rows += len(rows)
        kept: list[str] = []
        for row in rows:
            lower = row.lower()
            is_priority = any(
                tag in lower for tag in ("<td>critical</td>", "<td>refusal</td>", "<td>warning</td>")
            )
            if is_priority:
                kept.append(row + "</tr>")
                continue
            if defect_kept < DEFECT_HTML_EXAMPLES:
                kept.append(row + "</tr>")
                defect_kept += 1
        total_kept += len(kept)
        rebuilt.append("\n" + "\n".join(kept) + "\n</tbody>" + suffix)
    dropped = total_rows - total_kept
    result = "".join(rebuilt)
    if dropped > 0:
        note = (
            f"<p>Compacted on disk-full recovery: kept {total_kept} of {total_rows} rows "
            f"({dropped} defect rows omitted). Summary counts above are unchanged.</p>"
        )
        result = result.replace("<body>", "<body>\n" + note, 1)
    return result
