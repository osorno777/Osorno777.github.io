from pathlib import Path

from translation_qa.models import AuditResult, Finding, Severity
from translation_qa.report import compact_existing_reports, write_reports


def _result(n_defects: int = 20) -> AuditResult:
    findings = [
        Finding(
            check="structure.truncated",
            severity=Severity.CRITICAL,
            message="Translation is much shorter.",
            english="long english",
            translated="short",
        ),
        Finding(
            check="refusal.policy",
            severity=Severity.REFUSAL,
            message="I cannot assist",
            translated="I cannot assist with that religious content.",
        ),
        Finding(
            check="residual.english",
            severity=Severity.WARNING,
            message="English leftover",
            word="Christ",
        ),
    ]
    findings.extend(
        Finding(
            check="word.untranslated",
            severity=Severity.DEFECT,
            message=f"missing {i}",
            word=f"word{i}",
            english="The church must not bless state theft. " * 8,
            translated="x" * 400,
            sentence_index=i,
        )
        for i in range(n_defects)
    )
    return AuditResult(
        english_path="en.pdf",
        translated_path="es.html",
        language="es",
        findings=findings,
        sentences_compared=10,
        words_checked=100,
        words_unverified=2,
        english_pages=3,
        translated_pages=3,
    )


def test_compact_reports_write_html_first_without_csv(tmp_path: Path):
    result = _result(200)
    paths = write_reports(result, tmp_path, "btc-3__btc-3_da__da")
    assert "html" in paths
    assert "json" in paths
    assert "csv" not in paths
    assert not (tmp_path / "btc-3__btc-3_da__da.csv").exists()
    html = paths["html"].read_text(encoding="utf-8")
    assert "Critical: 1" in html
    assert "Defects: 200" in html
    assert "word.untranslated" in html
    assert html.count("<tr>") < 180
    payload = paths["json"].read_text(encoding="utf-8")
    assert '"findings"' not in payload
    assert "priority_findings" in payload
    assert "defect_checks" in payload
    assert '"word.untranslated":200' in payload


def test_full_reports_include_every_finding(tmp_path: Path):
    result = _result(12)
    paths = write_reports(result, tmp_path, "full", full=True)
    assert paths["csv"].exists()
    html = paths["html"].read_text(encoding="utf-8")
    assert html.count("<td>defect</td>") == 12
    payload = paths["json"].read_text(encoding="utf-8")
    assert '"findings"' in payload


def test_compact_existing_deletes_json_csv_and_shrinks_html(tmp_path: Path):
    result = _result(200)
    write_reports(result, tmp_path, "old", full=True)
    html_before = (tmp_path / "old.html").stat().st_size
    stats = compact_existing_reports(tmp_path)
    assert stats["deleted_json"] == 1
    assert stats["deleted_csv"] == 1
    assert not (tmp_path / "old.json").exists()
    assert not (tmp_path / "old.csv").exists()
    assert (tmp_path / "old.html").exists()
    assert stats["shrunk_html"] == 1
    assert (tmp_path / "old.html").stat().st_size < html_before
