# Translation veracity checker

Slow, sentence-aligned, word-by-word audit of Alertness Books translations against the English sources. It looks for the defects that remain after DeepSeek drafts and Grok/Claude cleanup: refusals, leftover English, dropped numbers and scripture, missing names, truncated books, and (optionally) missing word meanings.

This Cloud Agent cannot read files on your Windows PC. Copy this folder to the machine that has the PDFs, or run it there against:

- `C:\Users\dinam\Documents\Writing\...`
- `C:\Alertness AI\website books`

## Install

```bat
cd tools\translation_qa
py -m pip install -r requirements.txt
```

## Passwords

Do not put PDF passwords in git or in chat. Copy `.env.example` to `.env` and set:

```bat
PDF_PASSWORDS=password-one;password-two;password-three
```

Use the bookstore PDF passwords you already keep locally (BTC / SU / BTW / econ). The checker tries each password only in memory.

## One pair

```bat
py -m translation_qa check --english "C:\Users\dinam\Documents\Writing\John Cobin Writings\SUFFERING UNJUSTLY\Suffering Unjustly (2026).pdf" --translated "C:\Users\dinam\Documents\Writing\John Cobin Writings\SUFFERING UNJUSTLY\Padeciendo Injustamente (2026).pdf" --lang es --output reports
```

## Whole catalog (20 books × languages)

1. Copy `paths.example.json` to `paths.json`.
2. Keep or add every English source path.
3. Point `translations_dir` at `C:\Alertness AI\website books`.
4. Name translation files so the language is visible (`_es`, `(Spanish)`, a `de` folder, and so on).

```bat
py -m translation_qa scan --config paths.json --delay 1.5 --llm
```

`--llm` turns on the slow word-meaning judge. Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` (or xAI / OpenRouter / DeepSeek) in `.env`. Prefer a different model family than the one that produced the translation.

Trial run on the first 25 aligned sentences:

```bat
py -m translation_qa scan --config paths.json --max-sentences 25
```

## What it checks

1. **Book structure** — truncated PDFs, missing chapters, garbled encoding.
2. **Refusals** — “as an AI”, “I cannot assist”, policy blocks, `[unable to translate]`, repeated boilerplate.
3. **Residual English** — untranslated English clauses left in a non-English file.
4. **Numbers and citations** — years, counts, and scripture references (e.g. John 3:16) that disappear.
5. **Word-by-word coverage** — every English content word is examined; names, numbers, and citations must appear; short/long sentence ratios flag dropped or added clauses.
6. **Optional LLM judge** — one aligned sentence at a time, with `--delay`, asking whether each content word’s meaning is present, reversed, or refused.

Reports are written as HTML, CSV, and JSON under `reports/`.

## Tests

```bat
py -m pytest
```
