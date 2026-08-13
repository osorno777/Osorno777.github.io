from __future__ import annotations

import csv
import json
from html import escape
from pathlib import Path

from translation_qa.models import AuditResult, Finding


def write_reports(result: AuditResult, output_dir: Path, stem: str) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{stem}.json"
    csv_path = output_dir / f"{stem}.csv"
    html_path = output_dir / f"{stem}.html"
    json_path.write_text(json.dumps(_as_dict(result), ensure_ascii=False, indent=2), encoding="utf-8")
    _write_csv(csv_path, result.findings)
    html_path.write_text(_render_html(result), encoding="utf-8")
    return {"json": json_path, "csv": csv_path, "html": html_path}


def _as_dict(result: AuditResult) -> dict:
    return {
        "english_path": result.english_path,
        "translated_path": result.translated_path,
        "language": result.language,
        "sentences_compared": result.sentences_compared,
        "words_checked": result.words_checked,
        "words_unverified": result.words_unverified,
        "english_pages": result.english_pages,
        "translated_pages": result.translated_pages,
        "counts": result.counts,
        "findings": [
            {
                "check": item.check,
                "severity": item.severity.value,
                "message": item.message,
                "word": item.word,
                "sentence_index": item.sentence_index,
                "english": item.english,
                "translated": item.translated,
                "extra": item.extra,
            }
            for item in result.findings
        ],
    }


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


def _render_html(result: AuditResult) -> str:
    counts = result.counts
    rows = []
    for item in result.findings:
        rows.append(
            "<tr>"
            f"<td>{escape(item.severity.value)}</td>"
            f"<td>{escape(item.check)}</td>"
            f"<td>{escape(item.word)}</td>"
            f"<td>{item.sentence_index if item.sentence_index is not None else ''}</td>"
            f"<td>{escape(item.message)}</td>"
            f"<td>{escape(item.english[:280])}</td>"
            f"<td>{escape(item.translated[:280])}</td>"
            "</tr>"
        )
    body = "\n".join(rows) or "<tr><td colspan='7'>No findings.</td></tr>"
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Translation QA {escape(result.language)}</title>
<style>
body {{ font-family: Georgia, serif; margin: 2rem; }}
table {{ border-collapse: collapse; width: 100%; font-size: 0.92rem; }}
th, td {{ border: 1px solid #ccc; padding: 0.4rem 0.5rem; vertical-align: top; }}
th {{ background: #222; color: #fff; }}
tr:nth-child(even) {{ background: #f6f6f6; }}
.summary span {{ margin-right: 1rem; }}
</style></head><body>
<h1>Translation veracity report</h1>
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
<p>English: {escape(result.english_path)}<br>Translation: {escape(result.translated_path)}</p>
<table>
<thead><tr><th>Severity</th><th>Check</th><th>Word</th><th>#</th><th>Message</th><th>English</th><th>Translation</th></tr></thead>
<tbody>
{body}
</tbody></table>
</body></html>
"""
