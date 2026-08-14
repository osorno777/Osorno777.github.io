import zipfile
from pathlib import Path

from translation_qa.extract import extract_epub, looks_like_epub
from translation_qa.discover import collect_pdfs, discover_pairs, infer_language


def _write_epub(path: Path, body: str) -> None:
    container = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""
    opf = """<?xml version="1.0"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bid" version="3.0">
  <manifest>
    <item id="ch1" href="ch1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="ch1"/>
  </spine>
</package>
"""
    xhtml = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<html xmlns="http://www.w3.org/1999/xhtml"><body><p>'
        f"{body}"
        "</p></body></html>"
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip")
        archive.writestr("META-INF/container.xml", container)
        archive.writestr("OEBPS/content.opf", opf)
        archive.writestr("OEBPS/ch1.xhtml", xhtml)


def test_extract_epub_reads_spine(tmp_path: Path) -> None:
    path = tmp_path / "econ-nie_es.epub"
    _write_epub(path, "La nueva economia institucional es un primer.")
    assert looks_like_epub(path)
    document = extract_epub(path, language="es")
    assert "nueva economia institucional" in document.text


def test_discover_pairs_store_slug_epub(tmp_path: Path) -> None:
    english = tmp_path / "english"
    website = tmp_path / "website"
    english.mkdir()
    website.mkdir()
    (english / "New Institutional Economics.pdf").write_bytes(b"%PDF")
    _write_epub(website / "econ-nie_es.epub", "La nueva economia institucional.")
    assert infer_language(website / "econ-nie_es.epub") == "es"
    files = collect_pdfs([website])
    assert [path.name for path in files] == ["econ-nie_es.epub"]
    pairs = discover_pairs(
        {
            "english_dirs": [str(english)],
            "translations_dir": str(website),
            "peek_language": False,
        }
    )
    assert [(pair.book_id, pair.language) for pair in pairs] == [
        ("new-institutional-economics", "es")
    ]
