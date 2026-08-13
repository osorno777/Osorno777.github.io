from pathlib import Path

from translation_qa.discover import infer_book_id, infer_language


def test_infer_language_from_filename():
    assert infer_language(Path("Bearing the Cross (Spanish).pdf")) == "es"
    assert infer_language(Path("suffering_unjustly_de.pdf")) == "de"
    assert infer_language(Path("behind-the-walls-french.pdf")) == "fr"


def test_infer_book_id_strips_english_markers():
    book_id = infer_book_id(Path("Bearing the Cross (complete).pdf"))
    assert "bearing" in book_id
    assert "complete" not in book_id
