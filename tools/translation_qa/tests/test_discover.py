from pathlib import Path

from translation_qa.cli import main
from translation_qa.discover import (
    catalog_book_id,
    discover_pairs,
    infer_book_id,
    infer_language,
    select_english_sources,
    unmatched_translations,
)


def catalog_id(path):
    return catalog_book_id(path) or infer_book_id(path)


def _english(config):
    return select_english_sources(config)


def test_unmatched_lists_english_interiors(tmp_path):
    english = tmp_path / "Behind the Walls (2026).pdf"
    english.write_bytes(b"%PDF")
    translations = tmp_path / "website"
    translations.mkdir()
    junk = translations / "Behind the Walls INTERIOR BIODUP-DO-NOT-USE.pdf"
    junk.write_bytes(b"%PDF")
    leftover = unmatched_translations(
        {
            "english_sources": [str(english)],
            "translations_dir": str(translations),
        }
    )
    assert leftover
    assert "DO-NOT-USE" in leftover[0][1] or "English" in leftover[0][1]



def test_infer_language_from_filename():
    assert infer_language(Path("Bearing the Cross (Spanish).pdf")) == "es"
    assert infer_language(Path("suffering_unjustly_de.pdf")) == "de"
    assert infer_language(Path("behind-the-walls-french.pdf")) == "fr"


def test_english_interior_is_not_a_translation():
    assert infer_language(Path("Behind the Walls (2026) INTERIOR 396pp v3 FINAL.pdf")) == "en"


def test_infer_book_id_strips_english_markers():
    book_id = infer_book_id(Path("Bearing the Cross (complete).pdf"))
    assert "bearing" in book_id
    assert "complete" not in book_id


def test_discover_skips_pairing_a_file_with_itself(tmp_path):
    english = tmp_path / "Behind the Walls (2026).pdf"
    english.write_bytes(b"%PDF")
    config = {
        "english_sources": [str(english)],
        "translations_dir": str(tmp_path),
    }
    assert discover_pairs(config) == []


def test_discover_skips_english_interiors_and_do_not_use(tmp_path):
    english = tmp_path / "english" / "Behind the Walls (2026).pdf"
    english.parent.mkdir()
    english.write_bytes(b"%PDF")
    translations = tmp_path / "website"
    translations.mkdir()
    (translations / "Behind the Walls (2026) INTERIOR v2 BIODUP-DO-NOT-USE.pdf").write_bytes(b"%PDF")
    (translations / "Behind the Walls (2026) INTERIOR 396pp v3 FINAL.pdf").write_bytes(b"%PDF")
    spanish = translations / "Behind the Walls (Spanish).pdf"
    spanish.write_bytes(b"%PDF")
    pairs = discover_pairs(
        {
            "english_sources": [str(english)],
            "translations_dir": str(translations),
        }
    )
    assert [pair.translated.name for pair in pairs] == ["Behind the Walls (Spanish).pdf"]
    assert pairs[0].language == "es"


def test_discover_matches_spanish_title_alias(tmp_path):
    english = tmp_path / "Suffering Unjustly (2026).pdf"
    english.write_bytes(b"%PDF")
    translated = tmp_path / "Padeciendo Injustamente (2026).pdf"
    translated.write_bytes(b"%PDF")
    pairs = discover_pairs(
        {
            "english_sources": [str(english)],
            "reference_translations": [str(translated)],
        }
    )
    assert len(pairs) == 1
    assert pairs[0].book_id.startswith("suffering")


def test_english_dirs_finds_all_books(tmp_path):
    writing = tmp_path / "Writing"
    (writing / "Austrian Economics").mkdir(parents=True)
    (writing / "Life in Chile").mkdir()
    (writing / "Austrian Economics" / "Austrian Economics (complete).pdf").write_bytes(b"%PDF")
    (writing / "Life in Chile" / "Life in Chile (2026).pdf").write_bytes(b"%PDF")
    sources = select_english_sources({"english_dirs": [str(writing)]})
    names = sorted(path.name for path in sources)
    assert len(names) == 2
    assert any("Austrian" in name for name in names)
    assert any("Chile" in name for name in names)


def test_list_command_prints_pair_count(tmp_path, capsys):
    english = tmp_path / "Suffering Unjustly.pdf"
    translated = tmp_path / "Suffering Unjustly Spanish.pdf"
    english.write_bytes(b"%PDF")
    translated.write_bytes(b"%PDF")
    reports = tmp_path / "reports"
    config_path = tmp_path / "paths.json"
    config_path.write_text(
        '{"english_sources": ["%s"], "translations_dir": "%s", "output_dir": "%s"}'
        % (
            str(english).replace("\\", "/"),
            str(tmp_path).replace("\\", "/"),
            str(reports).replace("\\", "/"),
        ),
        encoding="utf-8",
    )
    assert main(["list", "--config", str(config_path)]) == 0
    output = capsys.readouterr().out
    assert "Translation pairs: 1" in output
    assert "es" in output
    assert (reports / "list.txt").is_file()


def test_spanish_de_is_not_german():
    assert infer_language(Path("Detrás de los Muros.pdf")) == "und"
    assert infer_language(Path("Detrás de los Muros (Spanish).pdf")) == "es"
    assert infer_book_id(Path("Detrás de los Muros.pdf")) == "behind-the-walls"


def test_isbn_maps_to_catalog_book():
    assert infer_book_id(Path("interior_9798905930942_es.pdf")) == "behind-the-walls"
    assert infer_language(Path("interior_9798905930942_es.pdf")) == "es"


def test_store_language_folder(tmp_path):
    english = tmp_path / "Austrian Economics.pdf"
    english.write_bytes(b"%PDF")
    folder = tmp_path / "website" / "Amharic"
    folder.mkdir(parents=True)
    translated = folder / "Austrian Economics.pdf"
    translated.write_bytes(b"%PDF")
    pairs = discover_pairs(
        {
            "english_sources": [str(english)],
            "translations_dir": str(tmp_path / "website"),
            "peek_language": False,
        }
    )
    assert len(pairs) == 1
    assert pairs[0].language == "am"


def test_btc_part_falls_back_to_complete_english(tmp_path):
    english = tmp_path / "Bearing the Cross (complete).pdf"
    english.write_bytes(b"%PDF")
    translated = tmp_path / "Bearing the Cross BOOK THREE Rancagua (Spanish).pdf"
    translated.write_bytes(b"%PDF")
    pairs = discover_pairs(
        {
            "english_sources": [str(english)],
            "reference_translations": [str(translated)],
            "peek_language": False,
        }
    )
    assert len(pairs) == 1
    assert pairs[0].language == "es"
    assert pairs[0].english.name.startswith("Bearing")


def test_austrian_primer_is_not_modern_themes_primer():
    assert infer_book_id(Path("Austrian Economics A Primer.pdf")) == "austrian-economics"
    assert infer_book_id(Path("A Primer on Modern Themes in Free Market Economics and Policy.pdf")) == (
        "primer-on-modern-themes"
    )


def test_list_returns_zero_when_no_pairs(tmp_path, capsys):
    english = tmp_path / "Life in Chile.pdf"
    english.write_bytes(b"%PDF")
    translations = tmp_path / "empty"
    translations.mkdir()
    reports = tmp_path / "reports"
    config_path = tmp_path / "paths.json"
    config_path.write_text(
        '{"english_sources": ["%s"], "translations_dir": "%s", "output_dir": "%s"}'
        % (
            str(english).replace("\\", "/"),
            str(translations).replace("\\", "/"),
            str(reports).replace("\\", "/"),
        ),
        encoding="utf-8",
    )
    assert main(["list", "--config", str(config_path)]) == 0
    assert "Translation pairs: 0" in capsys.readouterr().out


def test_scan_resumes_existing_report(tmp_path, capsys):
    english = tmp_path / "Suffering Unjustly.txt"
    translated = tmp_path / "Suffering Unjustly Spanish.txt"
    english.write_text("Christ suffered unjustly in 33. See John 19:16.", encoding="utf-8")
    translated.write_text("Cristo padecio injustamente en 33. Ver Juan 19:16.", encoding="utf-8")
    reports = tmp_path / "reports"
    config_path = tmp_path / "paths.json"
    config_path.write_text(
        '{"english_sources": ["%s"], "translations_dir": "%s", "output_dir": "%s", "peek_language": false}'
        % (
            str(english).replace("\\", "/"),
            str(tmp_path).replace("\\", "/"),
            str(reports).replace("\\", "/"),
        ),
        encoding="utf-8",
    )
    assert main(["scan", "--config", str(config_path)]) in {0, 1}
    html_files = list(reports.glob("*.html"))
    assert html_files
    first = html_files[0].read_text(encoding="utf-8")
    html_files[0].write_text(first + "\n<!-- marker -->\n", encoding="utf-8")
    capsys.readouterr()
    assert main(["scan", "--config", str(config_path)]) in {0, 1}
    output = capsys.readouterr().out
    assert "Resume skip" in output
    assert "<!-- marker -->" in html_files[0].read_text(encoding="utf-8")


def test_xml_named_pdf_is_skipped(tmp_path):
    english = tmp_path / "Behind the Walls (2026).pdf"
    english.write_bytes(b"%PDF")
    translations = tmp_path / "website"
    translations.mkdir()
    xml = translations / "Behind the Walls (Spanish).pdf"
    xml.write_bytes(b"<?xml version='1.0'?><catalog/>")
    real = translations / "Behind the Walls (French).pdf"
    real.write_bytes(b"%PDF")
    leftover = unmatched_translations(
        {
            "english_sources": [str(english)],
            "translations_dir": str(translations),
            "peek_language": False,
        }
    )
    reasons = " ".join(reason for _, reason in leftover)
    assert "xml" in reasons
    pairs = discover_pairs(
        {
            "english_sources": [str(english)],
            "translations_dir": str(translations),
            "peek_language": False,
        }
    )
    assert [pair.translated.name for pair in pairs] == ["Behind the Walls (French).pdf"]


def test_scan_continues_after_xml_file(tmp_path, capsys):
    english = tmp_path / "Suffering Unjustly.txt"
    xml = tmp_path / "Suffering Unjustly German.pdf"
    translated = tmp_path / "Suffering Unjustly Spanish.txt"
    english.write_text("Christ suffered unjustly in 33.", encoding="utf-8")
    xml.write_bytes(b"<?xml version='1.0'?><doc/>")
    translated.write_text("Cristo padecio injustamente en 33.", encoding="utf-8")
    reports = tmp_path / "reports"
    config_path = tmp_path / "paths.json"
    config_path.write_text(
        '{"english_sources": ["%s"], "translations_dir": "%s", "output_dir": "%s", "peek_language": false}'
        % (
            str(english).replace("\\", "/"),
            str(tmp_path).replace("\\", "/"),
            str(reports).replace("\\", "/"),
        ),
        encoding="utf-8",
    )
    assert main(["inventory", "--config", str(config_path)]) == 0
    inventory_out = capsys.readouterr().out
    assert "xml" in inventory_out
    assert main(["scan", "--config", str(config_path)]) in {0, 1}
    html_files = list(reports.glob("*.html"))
    assert html_files
    assert any("Spanish" in path.name or "es" in path.name for path in html_files)


def test_extract_sample_accepts_windows1252_txt(tmp_path):
    from translation_qa.extract import extract_sample

    path = tmp_path / "notes.txt"
    path.write_bytes("Padeciendo injustamente.\xad More text.".encode("cp1252"))
    sample = extract_sample(path)
    assert "Padeciendo" in sample


def test_discover_does_not_crash_on_latin1_txt(tmp_path):
    english = tmp_path / "Suffering Unjustly.pdf"
    english.write_bytes(b"%PDF")
    junk = tmp_path / "website"
    junk.mkdir()
    latin = junk / "Suffering Unjustly Spanish.txt"
    latin.write_bytes("Cristo padeci\xf3 injustamente.".encode("latin-1"))
    xml = junk / "catalog.pdf"
    xml.write_bytes(b"<?xml version='1.0'?><doc/>")
    pairs = discover_pairs(
        {
            "english_sources": [str(english)],
            "translations_dir": str(junk),
            "peek_language": True,
        }
    )
    assert len(pairs) == 1
    assert pairs[0].translated.name.endswith(".txt")


def test_kdp_public_choice_is_not_christian_theology(tmp_path):
    writing = tmp_path / "Writing"
    writing.mkdir()
    (writing / "Christian Theology of Public Policy.pdf").write_bytes(b"%PDF")
    (writing / "A Primer on Modern Themes in Free Market Economics and Policy.pdf").write_bytes(b"%PDF")
    website = tmp_path / "website"
    kdp = website / "PDF" / "kdp_by_isbn"
    kdp.mkdir(parents=True)
    (website / "03b_public_choice_primer.pdf").write_bytes(b"%PDF")
    af = kdp / "Public_Choice_A_Primer_AF_2026_ebook_979-8-90593-726-2.pdf"
    af.write_bytes(b"%PDF")
    paperback = kdp / "Public_Choice_A_Primer_AF_2026_paperback_979-8-90593-725-5.pdf"
    paperback.write_bytes(b"%PDF")
    config = {
        "english_dirs": [str(writing), str(website)],
        "translations_dir": str(website),
        "peek_language": False,
    }
    sources = {catalog_id(path): path.name for path in _english(config)}
    assert sources["public-choice"] == "03b_public_choice_primer.pdf"
    assert "christian-theology-of-public-policy" in sources
    pairs = discover_pairs(config)
    assert [(pair.book_id, pair.language) for pair in pairs] == [("public-choice", "af")]
    assert pairs[0].translated.name == af.name


def test_kdp_austrian_primer_is_not_modern_themes(tmp_path):
    writing = tmp_path / "Writing"
    writing.mkdir()
    (writing / "A Primer on Modern Themes in Free Market Economics and Policy.pdf").write_bytes(b"%PDF")
    website = tmp_path / "website"
    website.mkdir()
    (website / "03_austrian_economics_primer.pdf").write_bytes(b"%PDF")
    es = website / "Austrian_Economics_A_Primer_ES_2026_ebook.pdf"
    es.write_bytes(b"%PDF")
    pairs = discover_pairs(
        {
            "english_dirs": [str(writing), str(website)],
            "translations_dir": str(website),
            "peek_language": False,
        }
    )
    assert len(pairs) == 1
    assert pairs[0].book_id == "austrian-economics"
    assert pairs[0].language == "es"


def test_surviving_chilean_justice_is_not_life_in_chile(tmp_path):
    writing = tmp_path / "Writing"
    writing.mkdir()
    (writing / "Life in Chile.pdf").write_bytes(b"%PDF")
    website = tmp_path / "website"
    website.mkdir()
    (website / "05_surviving_chilean_justice.pdf").write_bytes(b"%PDF")
    es = website / "05_surviving_chilean_justice_es.pdf"
    es.write_bytes(b"%PDF")
    sources = select_english_sources(
        {"english_dirs": [str(writing), str(website)], "translations_dir": str(website)}
    )
    ids = {infer_book_id(path) for path in sources}
    assert "life-in-chile" in ids
    assert "surviving-chilean-justice" in ids
    pairs = discover_pairs(
        {
            "english_dirs": [str(writing), str(website)],
            "translations_dir": str(website),
            "peek_language": False,
        }
    )
    assert [(pair.book_id, pair.language) for pair in pairs] == [("surviving-chilean-justice", "es")]


def test_numbered_ai_finance_pairs_with_website_english(tmp_path):
    website = tmp_path / "website"
    website.mkdir()
    (website / "01_ai_augmented_personal_finance.pdf").write_bytes(b"%PDF")
    es = website / "01_ai_augmented_personal_finance_es.pdf"
    es.write_bytes(b"%PDF")
    pairs = discover_pairs(
        {
            "english_dirs": [str(website)],
            "translations_dir": str(website),
            "peek_language": False,
        }
    )
    assert len(pairs) == 1
    assert pairs[0].book_id == "ai-augmented-personal-finance"
    assert pairs[0].language == "es"
    assert pairs[0].english.name.startswith("01_")


def test_stf_short_code_pairs_sentenced_to_the_future(tmp_path):
    website = tmp_path / "website"
    epub = website / "EPUB"
    epub.mkdir(parents=True)
    (website / "Sentenced_to_the_Future_paperback_979-8-90593-987-7.pdf").write_bytes(b"%PDF")
    es = epub / "STF_es.pdf"
    es.write_bytes(b"%PDF")
    pairs = discover_pairs(
        {
            "english_dirs": [str(website)],
            "translations_dir": str(website),
            "peek_language": False,
        }
    )
    assert len(pairs) == 1
    assert pairs[0].book_id == "sentenced-to-the-future"
    assert pairs[0].language == "es"


def test_padeciendo_in_english_folder_is_still_a_translation(tmp_path):
    folder = tmp_path / "SUFFERING UNJUSTLY"
    folder.mkdir()
    english = folder / "Suffering Unjustly (2026).pdf"
    english.write_bytes(b"%PDF")
    translated = folder / "Padeciendo Injustamente (2026).pdf"
    translated.write_bytes(b"%PDF")
    pairs = discover_pairs(
        {
            "english_sources": [str(english)],
            "reference_translations": [str(translated)],
            "peek_language": False,
        }
    )
    assert len(pairs) == 1
    assert pairs[0].book_id == "suffering-unjustly"
    assert infer_language(translated) != "en"


def test_writing_junk_is_not_an_english_source(tmp_path):
    writing = tmp_path / "Writing"
    logs = writing / "Olders docs re kids" / "EA Games" / "The Sims 2" / "Logs"
    logs.mkdir(parents=True)
    (logs / "ObjectError_F001_t104404.txt").write_text("error", encoding="utf-8")
    (writing / "Harry Potter and the Sorcerer_s Stone.pdf").write_bytes(b"%PDF")
    (writing / "Austrian Economics.pdf").write_bytes(b"%PDF")
    sources = select_english_sources({"english_dirs": [str(writing)]})
    assert [path.name for path in sources] == ["Austrian Economics.pdf"]


def test_zh_hk_maps_to_traditional_chinese():
    assert infer_language(Path("Austrian_Economics_A_Primer_ZH-HK_2026_ebook.pdf")) == "zh-tw"


def test_prolife_english_pdf_is_not_a_translation(tmp_path):
    website = tmp_path / "website"
    website.mkdir()
    english = website / "prolife_policy.pdf"
    english.write_bytes(b"%PDF")
    es = website / "prolife_policy_es.pdf"
    es.write_bytes(b"%PDF")
    pairs = discover_pairs(
        {
            "english_dirs": [str(website)],
            "translations_dir": str(website),
            "peek_language": False,
        }
    )
    assert [(pair.book_id, pair.language) for pair in pairs] == [("pro-life-policy", "es")]
    leftover = unmatched_translations(
        {
            "english_dirs": [str(website)],
            "translations_dir": str(website),
            "peek_language": False,
        }
    )
    assert any(path.name == "prolife_policy.pdf" for path, _reason in leftover)
