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


def test_public_list_catalog_maps_slug_lang(tmp_path):
    english = tmp_path / "english"
    bookstore = tmp_path / "bookstore"
    public = bookstore / "public"
    out = bookstore / "fulfillment" / "_out"
    snapshot = bookstore / "_live_20260729-191923"
    english.mkdir()
    public.mkdir(parents=True)
    out.mkdir(parents=True)
    snapshot.mkdir()
    (english / "Bearing the Cross BOOK FIVE Casablanca part 2.pdf").write_bytes(b"%PDF")
    html = out / "btc-5_bn.html"
    html.write_text("<html><body><p>Bengali BTC 5.</p></body></html>", encoding="utf-8")
    (snapshot / "btc-5_bn.html").write_text("<html><body><p>old snapshot</p></body></html>", encoding="utf-8")
    catalog = public / "store_catalog.json"
    catalog.write_text(
        json.dumps(
            [
                {
                    "slug": "btc-5",
                    "lang": "bn",
                    "isbn": "979-8-90593-040-9",
                    "status": "hold",
                    "title": "BTC 5 BN",
                }
            ]
        ),
        encoding="utf-8",
    )
    (snapshot / "store_catalog.json").write_text(catalog.read_text(encoding="utf-8"), encoding="utf-8")
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
    snapshot_pairs = discover_pairs(
        {
            "english_dirs": [str(english)],
            "translations_dir": str(snapshot),
            "peek_language": False,
        }
    )
    assert all("_live_" not in str(pair.translated).replace("\\", "/") for pair in snapshot_pairs)


def test_contaminated_bak_and_stale_are_skipped(tmp_path):
    english = tmp_path / "english"
    out = tmp_path / "bookstore" / "fulfillment" / "_out"
    bak = tmp_path / "bookstore" / "fulfillment" / "_btc5_bak"
    english.mkdir()
    out.mkdir(parents=True)
    bak.mkdir(parents=True)
    (english / "Bearing the Cross BOOK FIVE Casablanca part 2.pdf").write_bytes(b"%PDF")
    (out / "btc-5_de.html").write_text("<html><body><p>clean de</p></body></html>", encoding="utf-8")
    (bak / "btc-5_de.CONTAMINATED-20260721b.html").write_text(
        "<html><body><p>contaminated</p></body></html>", encoding="utf-8"
    )
    stale = out / "btw_es_final.STALE-roberto-only.html"
    stale.write_text("<html><body><p>stale</p></body></html>", encoding="utf-8")
    pairs = discover_pairs(
        {
            "english_dirs": [str(english)],
            "translations_dir": str(tmp_path / "bookstore"),
            "peek_language": False,
        }
    )
    names = {pair.translated.name for pair in pairs}
    assert "btc-5_de.html" in names
    assert not any("CONTAMINATED" in name for name in names)
    assert not any("STALE" in name for name in names)


def test_stale_samples_folder_is_skipped(tmp_path):
    english = tmp_path / "english"
    out = tmp_path / "bookstore" / "fulfillment" / "_out"
    stale = out / "stale_samples"
    english.mkdir()
    stale.mkdir(parents=True)
    (english / "AI-Augmented Personal Finance.pdf").write_bytes(b"%PDF")
    (out / "econ-aifinance_pt.html").write_text("<html><body><p>live pt</p></body></html>", encoding="utf-8")
    (stale / "econ-aifinance_pt.html").write_text("<html><body><p>stale pt</p></body></html>", encoding="utf-8")
    pairs = discover_pairs(
        {
            "english_dirs": [str(english)],
            "translations_dir": str(tmp_path / "bookstore"),
            "peek_language": False,
        }
    )
    assert [pair.translated.parent.name for pair in pairs] == ["_out"]


def test_agter_die_mure_is_behind_the_walls_afrikaans():
    path = Path("Agter_die_Mure_AF_2026_ebook_9798905930027.epub")
    assert catalog_book_id(path) == "behind-the-walls"
    assert infer_language(path) == "af"


def test_btw_es_final_html_is_spanish():
    assert infer_language(Path("btw_es_final.html")) == "es"
    assert catalog_book_id(Path("btw_es_final.html")) == "behind-the-walls"


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
