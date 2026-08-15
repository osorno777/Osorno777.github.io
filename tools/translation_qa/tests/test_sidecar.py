import json
from pathlib import Path

import pytest

from translation_qa.discover import collect_pdfs, discover_pairs, select_english_sources
from translation_qa.extract import (
    SIDECAR_TEXT_WARNING,
    ExtractionError,
    extract_html,
    extract_plain,
    extract_sample,
    is_sidecar_contamination,
)
from translation_qa.pipeline import load_document


def _sidecar_json(path: Path) -> None:
    path.write_text(
        json.dumps({"text": "I cannot assist with that translation as an AI.", "status": "removed"}),
        encoding="utf-8",
    )


def test_json_sidecar_is_contamination(tmp_path):
    path = tmp_path / "econ-nie_es.json"
    _sidecar_json(path)
    assert is_sidecar_contamination(path)
    with pytest.raises(ExtractionError, match="contamination"):
        extract_plain(path)
    assert extract_sample(path) == ""
    with pytest.raises(ExtractionError, match="English master"):
        load_document(path, "es")


def test_txt_json_text_field_is_not_the_original(tmp_path):
    path = tmp_path / "vintage_linc_es.txt"
    _sidecar_json(path)
    assert is_sidecar_contamination(path)
    with pytest.raises(ExtractionError) as exc:
        extract_plain(path)
    assert SIDECAR_TEXT_WARNING in str(exc.value)


def test_sidecar_is_not_english_source_or_translation(tmp_path):
    english = tmp_path / "english"
    private = tmp_path / "bookstore" / "admin" / "translations" / "private"
    english.mkdir()
    private.mkdir(parents=True)
    (english / "New Institutional Economics.pdf").write_bytes(b"%PDF")
    html = private / "econ-nie_es.html"
    html.write_text("<html><body><p>La nueva economia institucional.</p></body></html>", encoding="utf-8")
    sidecar = private / "econ-nie_es.json"
    _sidecar_json(sidecar)
    named = private / "econ-nie_es.sidecar.txt"
    _sidecar_json(named)
    files = collect_pdfs([private])
    names = {path.name for path in files}
    assert "econ-nie_es.html" in names
    assert "econ-nie_es.json" not in names
    sources = select_english_sources(
        {
            "english_dirs": [str(english)],
            "english_sources": [str(sidecar)],
        }
    )
    assert all(path.suffix.lower() != ".json" for path in sources)
    pairs = discover_pairs(
        {
            "english_dirs": [str(english)],
            "translations_dir": str(private),
            "peek_language": False,
        }
    )
    assert [(pair.book_id, pair.language, pair.translated.name) for pair in pairs] == [
        ("new-institutional-economics", "es", "econ-nie_es.html")
    ]


def test_html_master_extracts_and_pairs_with_pdf_and_epub_separately(tmp_path):
    english = tmp_path / "english"
    website = tmp_path / "website"
    private = website / "admin" / "translations" / "private"
    english.mkdir()
    private.mkdir(parents=True)
    (english / "Life in Chile.pdf").write_bytes(b"%PDF")
    html = private / "vintage_linc_es.html"
    html.write_text("<html><body><h1>Vida en Chile</h1><p>Un guia.</p></body></html>", encoding="utf-8")
    document = extract_html(html, language="es")
    assert "Vida en Chile" in document.text
    pairs = discover_pairs(
        {
            "english_dirs": [str(english)],
            "translations_dir": str(website),
            "peek_language": False,
        }
    )
    assert [(pair.book_id, pair.language, pair.translated.suffix) for pair in pairs] == [
        ("life-in-chile", "es", ".html")
    ]


def test_fulfillment_rebuild_html_pairs_btc5(tmp_path):
    english = tmp_path / "english"
    rebuilds = tmp_path / "bookstore" / "fulfillment" / "_out" / "btc5_rebuilds"
    english.mkdir()
    rebuilds.mkdir(parents=True)
    (english / "Bearing the Cross BOOK FIVE Casablanca part 2.pdf").write_bytes(b"%PDF")
    (rebuilds / "btc-5_hi.html").write_text(
        "<html><body><p>Bearing the Cross book five Hindi rebuild.</p></body></html>",
        encoding="utf-8",
    )
    (rebuilds / "btc-5_ja.html").write_text(
        "<html><body><p>Bearing the Cross book five Japanese rebuild.</p></body></html>",
        encoding="utf-8",
    )
    (rebuilds / "btc-5_hi.json").write_text(
        '{"text": "I cannot assist with that translation as an AI."}',
        encoding="utf-8",
    )
    pairs = discover_pairs(
        {
            "english_dirs": [str(english)],
            "translations_dir": str(rebuilds),
            "peek_language": False,
        }
    )
    got = {(pair.book_id, pair.language, pair.translated.name) for pair in pairs}
    assert got == {
        ("bearing-the-cross-5", "hi", "btc-5_hi.html"),
        ("bearing-the-cross-5", "ja", "btc-5_ja.html"),
    }


def test_ordinary_translation_txt_is_not_a_sidecar(tmp_path):
    path = tmp_path / "econ-nie_es.txt"
    path.write_text("La nueva economia institucional es un primer.", encoding="utf-8")
    assert not is_sidecar_contamination(path)
    document = extract_plain(path, language="es")
    assert "economia institucional" in document.text
