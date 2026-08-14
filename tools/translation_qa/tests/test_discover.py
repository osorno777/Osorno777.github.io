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
    config_path = tmp_path / "paths.json"
    config_path.write_text(
        '{"english_sources": ["%s"], "translations_dir": "%s"}'
        % (str(english).replace("\\", "/"), str(tmp_path).replace("\\", "/")),
        encoding="utf-8",
    )
    assert main(["list", "--config", str(config_path)]) == 0
    output = capsys.readouterr().out
    assert "Translation pairs: 1" in output
    assert "es" in output
