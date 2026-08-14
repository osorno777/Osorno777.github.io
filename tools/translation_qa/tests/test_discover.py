from pathlib import Path

from translation_qa.cli import main
from translation_qa.discover import discover_pairs, infer_book_id, infer_language


def test_infer_language_from_filename():
    assert infer_language(Path("Bearing the Cross (Spanish).pdf")) == "es"
    assert infer_language(Path("suffering_unjustly_de.pdf")) == "de"
    assert infer_language(Path("behind-the-walls-french.pdf")) == "fr"


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
    assert "Found 1 pair" in output
    assert "es" in output



def test_infer_language_from_filename():
    assert infer_language(Path("Bearing the Cross (Spanish).pdf")) == "es"
    assert infer_language(Path("suffering_unjustly_de.pdf")) == "de"
    assert infer_language(Path("behind-the-walls-french.pdf")) == "fr"


def test_infer_book_id_strips_english_markers():
    book_id = infer_book_id(Path("Bearing the Cross (complete).pdf"))
    assert "bearing" in book_id
    assert "complete" not in book_id
