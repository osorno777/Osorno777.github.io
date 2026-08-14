"""Language codes used by KDP / Ingram / PublishDrive / Alertness Books filenames."""

from __future__ import annotations

import re

from translation_qa.textnorm import fold

LANGUAGE_NAMES: dict[str, str] = {
    "af": "Afrikaans",
    "am": "Amharic",
    "ar": "Arabic",
    "hy": "Armenian",
    "bg": "Bulgarian",
    "bn": "Bengali",
    "ca": "Catalan",
    "cs": "Czech",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "es": "Spanish",
    "et": "Estonian",
    "eu": "Basque",
    "fa": "Persian",
    "fi": "Finnish",
    "fr": "French",
    "ka": "Georgian",
    "gl": "Galician",
    "he": "Hebrew",
    "hi": "Hindi",
    "hr": "Croatian",
    "hu": "Hungarian",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "ln": "Lingala",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "ml": "Malayalam",
    "ms": "Malay",
    "nl": "Dutch",
    "no": "Norwegian",
    "pl": "Polish",
    "pt": "Portuguese",
    "pt-br": "Portuguese (Brazil)",
    "qu": "Quechua",
    "ro": "Romanian",
    "ru": "Russian",
    "sk": "Slovak",
    "sl": "Slovenian",
    "sr": "Serbian",
    "sv": "Swedish",
    "sw": "Swahili",
    "ta": "Tamil",
    "th": "Thai",
    "tl": "Tagalog",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "vi": "Vietnamese",
    "yo": "Yoruba",
    "zh": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)",
}

NAME_TO_CODE = {name.lower(): code for code, name in LANGUAGE_NAMES.items()}
NAME_TO_CODE.update(
    {
        "chinese": "zh",
        "chinese (simp.)": "zh",
        "chinese (simp)": "zh",
        "chinese simplified": "zh",
        "simplified chinese": "zh",
        "mandarin": "zh",
        "chinese (trad.)": "zh-tw",
        "chinese (trad)": "zh-tw",
        "chinese traditional": "zh-tw",
        "traditional chinese": "zh-tw",
        "brazilian portuguese": "pt-br",
        "portuguese brazilian": "pt-br",
        "castilian": "es",
        "espanol": "es",
        "espa\u00f1ol": "es",
        "deutsch": "de",
        "norsk": "no",
        "bokmal": "no",
        "bokm\u00e5l": "no",
        "bahasa indonesia": "id",
        "bahasa": "id",
        "kiswahili": "sw",
        "filipino": "tl",
        "tieng viet": "vi",
        "farsi": "fa",
    }
)

# Script samples beat Latin stopwords when enough characters are present.
_SCRIPTS: tuple[tuple[str, str, int], ...] = (
    ("ja", r"[\u3040-\u30ff]", 4),
    ("ko", r"[\uac00-\ud7af]", 6),
    ("zh", r"[\u4e00-\u9fff]", 8),
    ("ar", r"[\u0600-\u06ff]", 8),
    ("he", r"[\u0590-\u05ff]", 6),
    ("hi", r"[\u0900-\u097f]", 8),
    ("bn", r"[\u0980-\u09ff]", 6),
    ("ta", r"[\u0b80-\u0bff]", 6),
    ("ml", r"[\u0d00-\u0d7f]", 6),
    ("th", r"[\u0e00-\u0e7f]", 6),
    ("am", r"[\u1200-\u137f]", 6),
    ("ka", r"[\u10a0-\u10ff]", 6),
    ("hy", r"[\u0530-\u058f]", 6),
    ("el", r"[\u0370-\u03ff]", 6),
)

_CYRILLIC = re.compile(r"[\u0400-\u04ff]")
_LATIN_STOPWORDS: dict[str, frozenset[str]] = {
    "en": frozenset("the and of to in is that for as with on this are was be by from or an".split()),
    "es": frozenset("que los las una del para con por como mas pero sus una".split()),
    "fr": frozenset("les une des dans est que pour avec pas sont sur".split()),
    "de": frozenset("und der die das nicht ein eine ist den dem".split()),
    "it": frozenset("che non una per con sono della degli".split()),
    "pt": frozenset("que nao uma para com os as dos das".split()),
    "nl": frozenset("het van een dat niet op voor zijn".split()),
    "pl": frozenset("nie jest to sie czy jako przez".split()),
    "sv": frozenset("och det att som for inte har".split()),
    "da": frozenset("og det at som for ikke har".split()),
    "no": frozenset("og det at som for ikke har".split()),
    "fi": frozenset("ja on se etta joka ei ole".split()),
    "hu": frozenset("hogy nem egy egy a az".split()),
    "ro": frozenset("si este pentru din unei".split()),
    "cs": frozenset("ze je to na se pro jako".split()),
    "id": frozenset("yang dan tidak untuk dengan pada".split()),
    "tr": frozenset("ve bir icin degil bu da".split()),
    "vi": frozenset("va cua la khong trong mot".split()),
    "tl": frozenset("ang mga ng sa hindi na ay".split()),
    "sw": frozenset("na ya wa kwa si kwa".split()),
    "af": frozenset("die en van n is dat nie".split()),
    "yo": frozenset("ni ati pe ko si fun".split()),
    "ln": frozenset("na ya pe te mpe".split()),
    "qu": frozenset("kay pacha mana hinallataq".split()),
}


def detect_language_from_text(text: str) -> str:
    """Guess a language from extracted PDF text. Returns 'und' if unsure."""
    sample = (text or "")[:8000]
    if not sample.strip():
        return "und"

    for code, pattern, minimum in _SCRIPTS:
        if len(re.findall(pattern, sample)) >= minimum:
            if code == "zh" and ("繁" in sample or "體" in sample or "國" in sample[:400]):
                return "zh-tw"
            return code

    cyr = len(_CYRILLIC.findall(sample))
    if cyr >= 12:
        folded = fold(sample)
        uk_hits = sum(1 for word in ("ukrain", "що", "не") if word in sample.lower() or word in folded)
        if uk_hits >= 1 and "і" in sample:
            return "uk"
        return "ru"

    tokens = fold(sample).split()
    if len(tokens) < 12:
        return "und"
    best_code = "und"
    best_score = 2
    for code, words in _LATIN_STOPWORDS.items():
        score = sum(1 for token in tokens if token in words)
        if score > best_score:
            best_code = code
            best_score = score
    return best_code
