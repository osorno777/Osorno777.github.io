# Translation veracity checker

Slow, sentence-aligned, word-by-word audit of Alertness Books translations against the English sources. It looks for the defects that remain after DeepSeek drafts and Grok/Claude cleanup: refusals, leftover English, dropped numbers and scripture, missing names, truncated books, and (optionally) missing word meanings.

These files live in the GitHub repo, **not** in `C:\Users\dinam`. `cd tools\translation_qa` from your user home folder will fail until you download the repo first.

The checker **only reports problems**. It does not rewrite PDFs. Correction is a later step, after a full catalog report exists.

## Get the latest files onto this Windows PC

If the repo is already cloned at `C:\Users\dinam\Osorno777.github.io`:

```powershell
cd $HOME\Osorno777.github.io
git fetch origin cursor/translation-veracity-checker-5bc6:cursor/translation-veracity-checker-5bc6
git checkout cursor/translation-veracity-checker-5bc6
cd tools\translation_qa
.\rescan.bat
```

`rescan.bat` lists every catalog PDF it can see, writes `reports\list.txt` and `reports\inventory.tsv`, then scans. It skips pairs that already have a report, so you can stop and rerun.

If a scan is already printing the wrong book (for example Public Choice paired with Christian Theology of Public Policy), press Ctrl+C, `git pull` this branch, and run `.\rescan.bat` again.

If you do not have the clone yet:

```powershell
cd $HOME
git clone --branch cursor/translation-veracity-checker-5bc6 --single-branch https://github.com/osorno777/Osorno777.github.io.git
cd Osorno777.github.io\tools\translation_qa
.\setup.bat
.\rescan.bat
```

Zip fallback: https://github.com/osorno777/Osorno777.github.io/archive/refs/heads/cursor/translation-veracity-checker-5bc6.zip

## What it scans

The 20 Alertness Books store titles, including the five *Bearing the Cross* volumes, plus a complete BTC PDF when that is the English source:

- AI-Augmented Personal Finance
- Defending Your Ph.D. Dissertation
- Austrian Economics
- Public Choice
- New Institutional Economics
- Surviving Chilean Justice
- Suffering Unjustly
- Behind the Walls
- Bearing the Cross books 1-5 (Valparaiso / Rancagua / Casablanca)
- Sentenced to the Future
- Bible and Government
- Christian Theology of Public Policy
- A Primer on Modern Themes in Free Market Economics and Policy
- Building Regulation, Market Alternatives, and Allodial Policy
- Pro-Life Policy
- Life in Chile

English sources are the 20 catalog titles only. The checker looks for those English PDFs in the Writing folders *and* in `C:\Alertness AI\website books` (`01_*.pdf`, `*_EN_*_ebook_*.pdf`). Translations are walked from `C:\Alertness AI\website books`. Pairing uses ISBNs, numbered stems (`01_` through `05_`), catalog aliases (including accented Spanish titles), language folders (`Spanish`, `Amharic`, `es`), and filename tags (`_es`, `_ZH-HK`, `(French)`). It does not fuzzy-match shared words such as "primer", "chile", or "public policy" across different catalog books.

It skips Sims logs, `_freedom_data`, nohyph backups, audiobook silence logs, `DO-NOT-USE` / `BIODUP` files, and paperback KDP files when an ebook for the same book and language exists. It will not compare two English interiors of the same book.

## Install

`setup.bat` installs Python packages and copies `.env.example` to `.env` and `paths.example.json` to `paths.json`.

## Passwords

Do not put PDF passwords in git or in chat. Copy `.env.example` to `.env` and set:

```bat
PDF_PASSWORDS=password-one;password-two;password-three
```

Use the bookstore PDF passwords you already keep locally (BTC / SU / BTW / econ). The checker tries each password only in memory.

## Commands

```bat
py -m translation_qa inventory --config paths.json
py -m translation_qa list --config paths.json
py -m translation_qa scan --config paths.json
py -m translation_qa scan --config paths.json --force
py -m translation_qa scan --config paths.json --llm --delay 1.5
```

`--llm` turns on the slow word-meaning judge. The default judge is **Grok 4.6** (`XAI_MODEL=grok-4.6`). Set `XAI_API_KEY` in `.env`. A run without `--llm` only uses the deterministic checks.

Trial run on the first 25 aligned sentences:

```bat
py -m translation_qa scan --config paths.json --max-sentences 25
```

If `list` still shows only a few pairs, paste `tools\translation_qa\reports\list.txt` (filenames only) back into chat.

## What it checks

1. **Book structure** - truncated PDFs, missing chapters, garbled encoding.
2. **Refusals** - "as an AI", "I cannot assist", policy blocks, `[unable to translate]`, repeated boilerplate.
3. **Residual English** - untranslated English clauses left in a non-English file.
4. **Numbers and citations** - years, counts, and scripture references (e.g. John 3:16) that disappear.
5. **Word-by-word coverage** - every English content word is examined; names, numbers, and citations must appear; short/long sentence ratios flag dropped or added clauses.
6. **Optional LLM judge** - one aligned sentence at a time, with `--delay`, asking whether each content word's meaning is present, reversed, or refused.

Reports are written as HTML, CSV, and JSON under `reports/`.

## Tests

```bat
py -m pytest
```
