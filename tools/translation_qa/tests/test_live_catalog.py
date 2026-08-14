import json
from pathlib import Path

from translation_qa.discover import catalog_book_id, discover_pairs, infer_language, unmatched_translations
from translation_qa.live_catalog import artefact_lane, parse_store_catalog
from translation_qa.pipeline import audit_texts


def test_distributor_book5_filename_is_btc5():
    path = Path("Nest_Kriz_Book5_CS_2026_ebook_9798905931116.epub")
    assert catalog_book_id(path) == "bearing-the-cross-5"
    assert infer_language(path) == "cs"


def test_staging_is_not_storefront(tmp_path):
    english = tmp_path / "english"
    staging = tmp_path / "bookstore" / "_staging"
    private = tmp_path / "bookstore" / "admin" / "translations" / "private"
    english.mkdir()
    staging.mkdir(parents=True)
    private.mkdir(parents=True)
    (english / "Bearing the Cross BOOK FIVE Casablanca part 2.pdf").write_bytes(b"%PDF")
    (staging / "btc-5_bn.html").write_text("<html><body><p>staging</p></body></html>", encoding="utf-8")
    live = private / "btc-5_bn.html"
    live.write_text("<html><body><p>live bengali</p></body></html>", encoding="utf-8")
    pairs = discover_pairs(
        {
            "english_dirs": [str(english)],
            "translations_dirs": [str(tmp_path / "bookstore")],
            "peek_language": False,
        }
    )
    assert [(pair.language, pair.translated.parent.name) for pair in pairs] == [("bn", "private")]
    assert artefact_lane(live) == "live-storefront"
    assert artefact_lane(staging / "btc-5_bn.html") == "staging-not-storefront"


def test_store_catalog_points_at_private_html(tmp_path):
    english = tmp_path / "english"
    bookstore = tmp_path / "bookstore"
    private = bookstore / "admin" / "translations" / "private"
    english.mkdir()
    private.mkdir(parents=True)
    (english / "Bearing the Cross BOOK FIVE Casablanca part 2.pdf").write_bytes(b"%PDF")
    html = private / "btc-5_bn.html"
    html.write_text("<html><body><p>Bengali BTC 5 live.</p></body></html>", encoding="utf-8")
    catalog = bookstore / "store_catalog.json"
    catalog.write_text(
        json.dumps(
            {
                "btc-5": {
                    "bn": {
                        "isbn": "9798905931116",
                        "file": "/admin/translations/private/btc-5_bn.html",
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    assert parse_store_catalog(catalog) == [html]
    empty = tmp_path / "empty"
    empty.mkdir()
    pairs = discover_pairs(
        {
            "english_dirs": [str(english)],
            "translations_dir": str(empty),
            "store_catalog": str(catalog),
            "peek_language": False,
        }
    )
    assert [(pair.book_id, pair.language, pair.translated.name) for pair in pairs] == [
        ("bearing-the-cross-5", "bn", "btc-5_bn.html")
    ]


def test_unknown_language_is_not_clean(tmp_path):
    english = tmp_path / "Behind the Walls.pdf"
    mystery = tmp_path / "website" / "some_export.pdf"
    english.write_bytes(b"%PDF")
    mystery.parent.mkdir()
    mystery.write_bytes(b"%PDF")
    leftover = unmatched_translations(
        {
            "english_sources": [str(english)],
            "translations_dir": str(mystery.parent),
        }
    )
    assert leftover
    result = audit_texts("Hello.", "Hola.", "und")
    assert result.counts.get("critical", 0) >= 1
    assert any(item.check == "language.unknown" for item in result.findings)
