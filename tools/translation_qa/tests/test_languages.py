from translation_qa.languages import detect_language_from_text, NAME_TO_CODE


def test_store_languages_are_named():
    for name in ("amharic", "tagalog", "quechua", "yoruba", "lingala", "malayalam", "georgian", "armenian"):
        assert name in NAME_TO_CODE


def test_zh_hk_is_traditional_chinese():
    from pathlib import Path

    from translation_qa.discover import infer_language

    assert infer_language(Path("book_ZH-HK_ebook.pdf")) == "zh-tw"


def test_detect_spanish_and_chinese_and_arabic():
    spanish = "El sufrimiento puede ser injusto. Los cristianos padecen por la justicia y por la cruz."
    assert detect_language_from_text(spanish) == "es"
    chinese = "\u8fd9\u662f\u4e00\u672c\u5173\u4e8e\u5341\u5b57\u67b6\u7684\u4e66\u3002" * 4
    assert detect_language_from_text(chinese) == "zh"
    arabic = "\u0647\u0630\u0627 \u0643\u062a\u0627\u0628 \u0639\u0646 \u0627\u0644\u0635\u0644\u064a\u0628. " * 6
    assert detect_language_from_text(arabic) == "ar"
