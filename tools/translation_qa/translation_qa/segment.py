from __future__ import annotations

import re
from dataclasses import dataclass

_ABBREVIATIONS = {
    "mr",
    "mrs",
    "ms",
    "dr",
    "prof",
    "sr",
    "jr",
    "st",
    "rev",
    "gen",
    "col",
    "sgt",
    "vs",
    "etc",
    "e.g",
    "i.e",
    "cf",
    "pp",
    "vol",
    "no",
    "nos",
    "ch",
    "chap",
    "ed",
    "eds",
    "inc",
    "ltd",
    "approx",
    "al",
    "eng",
    "esp",
    "ital",
}

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+(?=[\"'“(\[]?[A-ZÁÉÍÓÚÜÑÀÈÌÒÙÄÖÅÆØÇ0-9])")
_WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ?-ž?-??-?\u4e00-\u9fff'’]+|\d+(?:[.,]\d+)?", re.UNICODE)
_SCRIPTURE_RE = re.compile(
    r"\b(?:[1-3]\s*)?"
    r"(?:Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|"
    r"Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalm|Psalms|Proverbs|Ecclesiastes|"
    r"Song|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|"
    r"Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|"
    r"Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|"
    r"Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation|"
    r"Gen|Exod|Ex|Lev|Num|Deut|Josh|Judg|Sam|Kgs|Chr|Neh|Esth|Ps|Prov|Eccl|Isa|"
    r"Jer|Lam|Ezek|Dan|Hos|Obad|Mic|Nah|Hab|Zeph|Hag|Zech|Mal|Matt|Rom|Cor|Gal|"
    r"Eph|Phil|Col|Thess|Tim|Phlm|Heb|Jas|Pet|Rev)"
    r"\.?\s+\d+:\d+(?:\s*[-–]\s*\d+)?\b",
    re.IGNORECASE,
)

ENGLISH_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "that", "this",
    "these", "those", "to", "of", "in", "on", "for", "from", "by", "with", "as",
    "at", "into", "over", "after", "before", "between", "through", "during",
    "without", "within", "about", "against", "is", "are", "was", "were", "be",
    "been", "being", "am", "do", "does", "did", "done", "have", "has", "had",
    "having", "will", "would", "shall", "should", "can", "could", "may", "might",
    "must", "not", "no", "nor", "so", "such", "too", "very", "just", "only",
    "also", "even", "still", "yet", "already", "here", "there", "when", "where",
    "why", "how", "what", "which", "who", "whom", "whose", "it", "its", "itself",
    "he", "him", "his", "she", "her", "hers", "they", "them", "their", "theirs",
    "we", "us", "our", "ours", "you", "your", "yours", "i", "me", "my", "mine",
    "one", "two", "some", "any", "each", "every", "all", "both", "few", "more",
    "most", "other", "another", "own", "same", "than", "because", "while",
    "although", "though", "whether", "until", "unless", "once", "upon",
}


@dataclass(frozen=True)
class Token:
    text: str
    start: int
    end: int
    kind: str  # word, number, scripture, other


def split_sentences(text: str) -> list[str]:
    compact = re.sub(r"[ \t]+", " ", text.replace("\u00a0", " ")).strip()
    if not compact:
        return []
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", compact) if part.strip()]
    sentences: list[str] = []
    for paragraph in paragraphs:
        paragraph = re.sub(r"\n+", " ", paragraph)
        pieces = _SENTENCE_SPLIT.split(paragraph)
        buffer = ""
        for piece in pieces:
            candidate = f"{buffer} {piece}".strip() if buffer else piece.strip()
            if _ends_with_abbreviation(candidate):
                buffer = candidate
                continue
            if candidate:
                sentences.append(candidate)
            buffer = ""
        if buffer:
            sentences.append(buffer)
    return sentences


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    for match in _WORD_RE.finditer(text):
        value = match.group(0)
        kind = "number" if value.replace(",", "").replace(".", "").isdigit() else "word"
        tokens.append(Token(text=value, start=match.start(), end=match.end(), kind=kind))
    for match in _SCRIPTURE_RE.finditer(text):
        tokens.append(Token(text=match.group(0), start=match.start(), end=match.end(), kind="scripture"))
    tokens.sort(key=lambda item: (item.start, item.end))
    return tokens


def content_words(text: str) -> list[Token]:
    words: list[Token] = []
    for token in tokenize(text):
        if token.kind == "scripture":
            words.append(token)
            continue
        if token.kind == "number":
            words.append(token)
            continue
        folded = token.text.lower().replace("’", "'")
        if folded in ENGLISH_STOPWORDS:
            continue
        if len(folded) <= 1:
            continue
        words.append(token)
    return words


def extract_scripture_refs(text: str) -> list[str]:
    return [match.group(0).strip() for match in _SCRIPTURE_RE.finditer(text)]


def _ends_with_abbreviation(text: str) -> bool:
    match = re.search(r"([A-Za-z.]+)\.$", text)
    if not match:
        return False
    token = match.group(1).rstrip(".").lower()
    return token in _ABBREVIATIONS
