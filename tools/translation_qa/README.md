# Translation veracity checker

Slow, sentence-aligned, word-by-word audit of Alertness Books translations against the English sources. It looks for the defects that remain after DeepSeek drafts and Grok/Claude cleanup: refusals, leftover English, dropped numbers and scripture, missing names, truncated books, and (optionally) missing word meanings.

These files live in the GitHub repo, **not** in `C:\Users\dinam`. `cd tools\translation_qa` from your user home folder will fail until you download the repo first.

## Get the files onto this Windows PC

In PowerShell, from `C:\Users\dinam`:

```powershell
cd $HOME
git clone --branch cursor/translation-veracity-checker-03d4 --single-branch https://github.com/osorno777/Osorno777.github.io.git
cd Osorno777.github.io\tools\translation_qa
.\setup.bat
```

If `git` is not installed, download the zip instead:

https://github.com/osorno777/Osorno777.github.io/archive/refs/heads/cursor/translation-veracity-checker-03d4.zip

Extract it, then:

```powershell
cd $HOME\Downloads\Osorno777.github.io-cursor-translation-veracity-checker-03d4\tools\translation_qa
.\setup.bat
```

The zip extract folder name can differ slightly. If `cd` fails, open File Explorer, search for `setup.bat` inside the extracted folder, then Shift+right-click that folder and choose **Open PowerShell window here**.

## Install

`setup.bat` installs Python packages and copies `.env.example` to `.env` and `paths.example.json` to `paths.json`. Or do it by hand:

```bat
cd Osorno777.github.io\tools\translation_qa
py -m pip install -r requirements.txt
copy .env.example .env
copy paths.example.json paths.json
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

## Whole catalog (all books × languages)

`paths.example.json` now scans:

- English PDFs under `C:\Users\dinam\Documents\Writing`
- Translations under `C:\Alertness AI\website books`

It skips `DO-NOT-USE` / `BIODUP` files and will not compare two English interiors of the same book.

After `git pull`, copy the new example over your old config, then list pairs before scanning:

```bat
copy /Y paths.example.json paths.json
py -m translation_qa list --config paths.json
py -m translation_qa scan --config paths.json
```

`list` should show far more than 3 pairs. If a translation is missing, put the language in the filename or folder (`_es`, `(Spanish)`, or an `es` folder).

```bat
py -m translation_qa scan --config paths.json --delay 1.5 --llm
```

`--llm` turns on the slow word-meaning judge. The default judge is **Grok 4.6** (`XAI_MODEL=grok-4.6`). Set `XAI_API_KEY` in `.env`. The current trial without `--llm` only runs the deterministic checks (refusals, numbers, leftover English, names).

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
