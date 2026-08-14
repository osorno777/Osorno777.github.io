"""Canonical Alertness Books catalog used to pair English sources with translations.

Titles, store slugs, and ISBNs are taken from https://alertnessbooks.com/store.php
(also served at alertnessai.com/AlertnessBooks). The store lists 20 book titles
in up to 40 languages, including English. Not every title is translated into
every language. Audiobooks are separate products and are not scanned.

Live store (2026-08-14): 20 English ebooks, about 537 non-English ebooks,
and about 67 audiobooks. Unique ebook ISBNs are about 557, which matches the
"about 550 products" bookstore figure when audiobooks are counted separately.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Book:
    id: str
    title: str
    aliases: tuple[str, ...]
    isbns: tuple[str, ...] = ()
    family: str = ""
    fallback: str = ""


# 20 current store titles. Longer aliases are preferred during matching.
BOOKS: tuple[Book, ...] = (
    Book(
        id="ai-augmented-personal-finance",
        title="AI-Augmented Personal Finance",
        aliases=(
            "ai-augmented personal finance",
            "ai augmented personal finance",
            "aifin",
            "finanzas personales con ia",
            "finanzas personales aumentadas",
            "field guide for liberty-minded investors",
            "01 ai augmented",
            "econ-aifinance",
            "econ aifinance",
        ),
        isbns=("9798905935275", "9798906195586"),
    ),
    Book(
        id="defending-your-phd-dissertation",
        title="Defending Your Ph.D. Dissertation",
        aliases=(
            "defending your ph d dissertation",
            "defending your phd dissertation",
            "hostile-reading survival guide",
            "hostile reading survival guide",
            "defendiendo tu tesis",
            "tesis doctoral",
            "02 defending your phd",
            "econ-phd",
            "econ phd",
        ),
        isbns=("9798905935305", "9798906191076"),
    ),
    Book(
        id="austrian-economics",
        title="Austrian Economics",
        aliases=(
            "austrian economics a primer",
            "austrian economics primer",
            "austrian economics",
            "economia austriaca",
            "primer for the liberty-minded reader",
            "liberty-minded reader",
            "03 austrian economics",
            "econ-austrian",
            "econ austrian",
        ),
        isbns=("9798905935336", "9798905935350"),
    ),
    Book(
        id="public-choice",
        title="Public Choice",
        aliases=(
            "public choice a primer",
            "public choice primer",
            "public choice",
            "eleccion publica",
            "primer for the politically sober",
            "politically sober",
            "03b public choice",
            "econ-publicchoice",
            "econ publicchoice",
        ),
        isbns=("9798905935367", "9798905935381"),
    ),
    Book(
        id="new-institutional-economics",
        title="New Institutional Economics",
        aliases=(
            "new institutional economics a primer",
            "new institutional economics primer",
            "new institutional economics",
            "nueva economia institucional",
            "primer on the rules of the game",
            "04 new institutional",
            "econ-nie",
            "econ nie",
        ),
        isbns=("9798905935398", "9798906195579"),
    ),
    Book(
        id="surviving-chilean-justice",
        title="Surviving Chilean Justice",
        aliases=(
            "surviving chilean justice",
            "sobreviviendo a la justicia chilena",
            "justicia chilena",
            "political persecution",
            "05 surviving chilean",
            "econ-survivingcj",
            "survivingcj",
        ),
        isbns=("9798905935428", "9798906195371"),
    ),
    Book(
        id="suffering-unjustly",
        title="Suffering Unjustly",
        aliases=(
            "suffering unjustly",
            "padeciendo injustamente",
            "padeciendo",
            "sufrimiento injusto",
        ),
        isbns=("9798905930911", "9798905930935"),
        family="su",
    ),
    Book(
        id="behind-the-walls",
        title="Behind the Walls",
        aliases=(
            "behind the walls",
            "detras de los muros",
            "detras de las paredes",
            "dietro i muri",
            "derriere les murs",
            "hinter den mauern",
        ),
        isbns=("9798905930942", "9798905930966"),
        family="btw",
    ),
    Book(
        id="bearing-the-cross-1",
        title="Bearing the Cross  -  BOOK ONE: Valparaiso (part 1)",
        aliases=(
            "bearing the cross book one",
            "bearing the cross book 1",
            "btc book one",
            "btc1",
            "btc-1",
            "valparaiso part 1",
            "valparaiso (part 1)",
        ),
        isbns=("9798905930973", "9798905930997"),
        family="btc",
        fallback="bearing-the-cross",
    ),
    Book(
        id="bearing-the-cross-2",
        title="Bearing the Cross  -  BOOK TWO: Valparaiso (part 2)",
        aliases=(
            "bearing the cross book two",
            "bearing the cross book 2",
            "btc book two",
            "btc2",
            "btc-2",
            "valparaiso part 2",
            "valparaiso (part 2)",
        ),
        isbns=("9798905931000", "9798905931024"),
        family="btc",
        fallback="bearing-the-cross",
    ),
    Book(
        id="bearing-the-cross-3",
        title="Bearing the Cross  -  BOOK THREE: Valparaiso (part 3) and Rancagua",
        aliases=(
            "bearing the cross book three",
            "bearing the cross book 3",
            "btc book three",
            "btc3",
            "btc-3",
            "valparaiso part 3",
            "rancagua",
        ),
        isbns=("9798905931031", "9798905931055"),
        family="btc",
        fallback="bearing-the-cross",
    ),
    Book(
        id="bearing-the-cross-4",
        title="Bearing the Cross  -  BOOK FOUR: Casablanca (part 1)",
        aliases=(
            "bearing the cross book four",
            "bearing the cross book 4",
            "btc book four",
            "btc4",
            "btc-4",
            "casablanca part 1",
            "casablanca (part 1)",
        ),
        isbns=("9798905931062", "9798905931086"),
        family="btc",
        fallback="bearing-the-cross",
    ),
    Book(
        id="bearing-the-cross-5",
        title="Bearing the Cross  -  BOOK FIVE: Casablanca (part 2)",
        aliases=(
            "bearing the cross book five",
            "bearing the cross book 5",
            "btc book five",
            "btc5",
            "btc-5",
            "casablanca part 2",
            "casablanca (part 2)",
        ),
        isbns=("9798905931093", "9798905931116"),
        family="btc",
        fallback="bearing-the-cross",
    ),
    Book(
        id="bearing-the-cross",
        title="Bearing the Cross (complete)",
        aliases=(
            "bearing the cross complete",
            "bearing the cross",
            "llevando la cruz",
            "cargando la cruz",
            "portant la croix",
            "portando la croce",
        ),
        isbns=(),
        family="btc",
    ),
    Book(
        id="sentenced-to-the-future",
        title="Sentenced to the Future",
        aliases=(
            "sentenced to the future",
            "condenado al futuro",
            "sentenced to future",
            "stf",
        ),
        isbns=("9798905939860", "9798905939853"),
    ),
    Book(
        id="bible-and-government",
        title="Bible and Government",
        aliases=(
            "bible and government",
            "bible and goverment",
            "biblia y gobierno",
            "public policy from a christian perspective",
            "vintage_bg",
            "vintage bg",
        ),
        isbns=("9798906193490", "9798906191212", "0972541802"),
    ),
    Book(
        id="christian-theology-of-public-policy",
        title="Christian Theology of Public Policy",
        aliases=(
            "christian theology of public policy",
            "teologia cristiana de la politica publica",
            "highlighting the american experience",
            "ctpp",
            "vintage_ctpp",
            "vintage ctpp",
        ),
        isbns=("9798906194107", "9798906191090", "0972975497"),
    ),
    Book(
        id="primer-on-modern-themes",
        title="A Primer on Modern Themes in Free Market Economics and Policy",
        aliases=(
            "primer on modern themes",
            "modern themes in free market",
            "free market economics and policy",
            "vintage_primer",
            "vintage primer",
            "vintage_pp",
            "vintage pp",
        ),
        isbns=("9798906195388", "9798906191168", "9798906195562"),
    ),
    Book(
        id="building-regulation-allodial-policy",
        title="Building Regulation, Market Alternatives, and Allodial Policy",
        aliases=(
            "building regulation",
            "allodial policy",
            "market alternatives and allodial",
            "vintage_breg",
            "vintage breg",
            "vintage_bldreg",
            "vintage bldreg",
        ),
        isbns=("9798906194510", "9798906191182"),
    ),
    Book(
        id="pro-life-policy",
        title="Pro-Life Policy",
        aliases=(
            "pro-life policy",
            "pro life policy",
            "prolife policy",
            "politica pro vida",
            "liberty and human rights",
            "vintage_prolife",
            "vintage prolife",
        ),
        isbns=("9798905939778", "9798906195692"),
    ),
    Book(
        id="life-in-chile",
        title="Life in Chile",
        aliases=(
            "life in chile",
            "vida en chile",
            "cautionary guide for newcomers",
            "vintage_linc",
            "vintage linc",
        ),
        isbns=("9798905939761", "9798905935329"),
    ),
)

BOOKS_BY_ID = {book.id: book for book in BOOKS}

# Short codes that should only match when they appear as their own token.
SHORT_CODES = {
    "btc": "bearing-the-cross",
    "btw": "behind-the-walls",
    "su": "suffering-unjustly",
    "nie": "new-institutional-economics",
    "ctpp": "christian-theology-of-public-policy",
    "aifin": "ai-augmented-personal-finance",
    "stf": "sentenced-to-the-future",
}

# Translated titles that may have no ISO language tag in the filename.
# Keep this list ASCII so Windows Python can import the file.
# Do not put English SKU aliases here (econ-aifinance, prolife policy, 01_).
FOREIGN_TITLE_ALIASES: tuple[str, ...] = (
    "padeciendo injustamente",
    "padeciendo",
    "detras de los muros",
    "detras de las paredes",
    "dietro i muri",
    "derriere les murs",
    "hinter den mauern",
    "llevando la cruz",
    "cargando la cruz",
    "portant la croix",
    "portando la croce",
    "finanzas personales",
    "defendiendo tu tesis",
    "economia austriaca",
    "eleccion publica",
    "nueva economia institucional",
    "sobreviviendo a la justicia chilena",
    "condenado al futuro",
    "biblia y gobierno",
    "teologia cristiana",
    "politica pro vida",
    "vida en chile",
    "la vida en chile",
)

# Numbered website-book stems (01_ / 03b_ / 05_). Longer prefixes must come first.
NUMBERED_STEMS: tuple[tuple[str, str], ...] = (
    ("03b", "public-choice"),
    ("01", "ai-augmented-personal-finance"),
    ("02", "defending-your-phd-dissertation"),
    ("03", "austrian-economics"),
    ("04", "new-institutional-economics"),
    ("05", "surviving-chilean-justice"),
)
