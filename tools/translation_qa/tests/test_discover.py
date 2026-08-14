from pathlib import Path

from translation_qa.cli import main
from translation_qa.discover import (
    discover_pairs,
    infer_book_id,
    infer_language,
    select_english_sources,
    unmatched_translations,
)


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
