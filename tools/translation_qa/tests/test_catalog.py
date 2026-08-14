from pathlib import Path

from translation_qa.catalog import BOOKS
from translation_qa.discover import catalog_book_id, infer_book_id


def test_catalog_source_is_utf8():
    path = Path(__file__).resolve().parents[1] / "translation_qa" / "catalog.py"
    path.read_text(encoding="utf-8")
    ids = {book.id for book in BOOKS}
    assert "bearing-the-cross" in ids
    store_ids = ids - {"bearing-the-cross"}
    assert len(store_ids) == 20


def test_all_twenty_english_filenames_resolve():
    samples = {
        "AI-Augmented Personal Finance.pdf": "ai-augmented-personal-finance",
        "Defending Your Ph.D. Dissertation.pdf": "defending-your-phd-dissertation",
        "Austrian Economics.pdf": "austrian-economics",
        "Public Choice.pdf": "public-choice",
        "New Institutional Economics.pdf": "new-institutional-economics",
        "Surviving Chilean Justice.pdf": "surviving-chilean-justice",
        "Suffering Unjustly.pdf": "suffering-unjustly",
        "Behind the Walls.pdf": "behind-the-walls",
        "Bearing the Cross BOOK ONE Valparaiso part 1.pdf": "bearing-the-cross-1",
        "Bearing the Cross BOOK TWO Valparaiso part 2.pdf": "bearing-the-cross-2",
        "Bearing the Cross BOOK THREE Rancagua.pdf": "bearing-the-cross-3",
        "Bearing the Cross BOOK FOUR Casablanca part 1.pdf": "bearing-the-cross-4",
        "Bearing the Cross BOOK FIVE Casablanca part 2.pdf": "bearing-the-cross-5",
        "Sentenced to the Future.pdf": "sentenced-to-the-future",
        "Bible and Government.pdf": "bible-and-government",
        "Christian Theology of Public Policy.pdf": "christian-theology-of-public-policy",
        "A Primer on Modern Themes in Free Market Economics and Policy.pdf": "primer-on-modern-themes",
        "Building Regulation Market Alternatives and Allodial Policy.pdf": "building-regulation-allodial-policy",
        "Pro-Life Policy.pdf": "pro-life-policy",
        "Life in Chile.pdf": "life-in-chile",
    }
    for name, book_id in samples.items():
        assert infer_book_id(Path(name)) == book_id, name


def test_isbn_catalog_match():
    assert catalog_book_id(Path("kdp_9798905935367_fr.pdf")) == "public-choice"


def test_numbered_website_stems():
    assert catalog_book_id(Path("01_ai_augmented_personal_finance_es.pdf")) == "ai-augmented-personal-finance"
    assert catalog_book_id(Path("03_austrian_economics_primer.pdf")) == "austrian-economics"
    assert catalog_book_id(Path("03b_public_choice_primer.pdf")) == "public-choice"
    assert catalog_book_id(Path("05_surviving_chilean_justice.pdf")) == "surviving-chilean-justice"
    assert catalog_book_id(Path("STF_es.pdf")) == "sentenced-to-the-future"
    assert catalog_book_id(Path("prolife_policy.pdf")) == "pro-life-policy"
    assert catalog_book_id(Path("prolife_policy_es.pdf")) == "pro-life-policy"


def test_kdp_public_choice_filename():
    assert (
        catalog_book_id(Path("Public_Choice_A_Primer_AF_2026_ebook_979-8-90593-726-2.pdf"))
        == "public-choice"
    )
    assert (
        catalog_book_id(Path("Austrian_Economics_A_Primer_ES_2026_ebook.pdf"))
        == "austrian-economics"
    )


def test_store_slugs_resolve():
    assert catalog_book_id(Path("vintage_bg_de.pdf")) == "bible-and-government"
    assert catalog_book_id(Path("vintage_bg_es.pdf")) == "bible-and-government"
    assert catalog_book_id(Path("vintage_ctpp_fr.pdf")) == "christian-theology-of-public-policy"
    assert catalog_book_id(Path("vintage_linc_es.pdf")) == "life-in-chile"
    assert catalog_book_id(Path("vintage_prolife_it.pdf")) == "pro-life-policy"
    assert catalog_book_id(Path("vintage_bldreg_pt.pdf")) == "building-regulation-allodial-policy"
    assert catalog_book_id(Path("vintage_pp_es.pdf")) == "primer-on-modern-themes"
    assert catalog_book_id(Path("econ-survivingcj_yo.pdf")) == "surviving-chilean-justice"
    assert catalog_book_id(Path("econ-nie_am.pdf")) == "new-institutional-economics"
    assert catalog_book_id(Path("btc-1_af.pdf")) == "bearing-the-cross-1"
