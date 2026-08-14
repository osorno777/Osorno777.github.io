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

If a scan is already printing the **correct** 152-pair KDP PDF catalog, leave it running. Resume skips HTML reports already written. Only stop it if it is pairing the wrong books.

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

English sources are the 20 catalog titles only. The Alertness Books store sells those 20 titles in **up to 40 languages** (not 20), including English. Not every book is translated into every language. The live store has about **537 non-English ebooks** plus 20 English ebooks (about 557 unique ebook ISBNs, the "about 550 products" figure) and about 67 audiobooks. Audiobooks are not scanned. IngramSpark has no audiobook programme (print and ebook only), so an audiobook fulfilment route is inert there.

## Bookstore relay (2026-08-13 13:30) -- checker implications only

`bookstore/WORKORDERS_RELAY_20260813_1330.md` supersedes earlier bookstore-lane orders. That file is **not** in this GitHub Pages repo. This checker honors it as follows and does **not** duplicate those other lanes:

- **Sidecar `text` field:** that field is the contamination that was removed, not the original it replaced. The original was never generated and does not exist in those files. Repair goes through the English master, never the sidecar. The checker refuses to read sidecar JSON / `text` as English or as a translation (`fix_refusal_text.py` already says the same in the bookstore clone).
- **Pipeline is hardened:** CC-Translate landed it in `translate_html.py` (task #58), tested on the known-bad strings with zero false positives. Rebuilds are safe. Do not duplicate that work, and do not treat rebuilds as unsafe.
- **Live storefront files:** the store serves `store_catalog.json` -> `/admin/translations/private/`. That is the fourth artefact (not `kdp_by_isbn`, not `_staging`). `btc-5_bn.html` in that folder is what a customer downloading Bengali BTC 5 actually received. The checker now reads `store_catalog.json` when present, labels inventory rows `live-storefront` vs `kdp-not-storefront` / `rebuild-not-storefront` / `staging-not-storefront`, and skips `_staging`.
- **Unknown language is not clean.** A file with no language tag is unmatched or flagged critical. It does not pass.
- **Distributor filenames** such as `Nest_Kriz_Book5_CS_2026_ebook_....epub` map to BTC book 5 + Czech. Do not duplicate `lineage_detect.py`, `qr_fix/fix_refusal_text.py`, `preflight_book_gate.py`, or `verify_fix_landed.py` -- those already exist in the bookstore clone.
- **Stand down (already sent):** Ingram cancellation for 19 live contaminated titles, and StreetLib 38-ISBN consolidation. This repo does not send those. CC-KDP only watches for the Ingram reply and confirms the 19 flip to Cancelled.
- **Life in Chile consultation:** included when the buyer has paid the full price -- one full-list purchase, or paperback + ebook, or the audiobook. Added route, not an Ingram-only replacement. Same wording for every channel. Do not present the audiobook clause as something Ingram can fulfil.

Confirmed on this Windows PC (3518 local hits, 2026-08-14):

- Live/rebuild HTML: `C:\Alertness AI\bookstore\fulfillment\_out` (including `btc5_rebuilds`, `btc12_tablefix`)
- BTW/BTC EPUBs: `C:\Alertness AI\bookstore\btw_rerender`
- Workorder: `C:\Alertness AI\bookstore\WORKORDERS_RELAY_20260813_1330.md`
- Refusal tool: `C:\Alertness AI\bookstore\qr_fix\fix_refusal_text.py`
- Not live: `fulfillment\*_bak`, `CONTAMINATED`, `STALE`, and `_safety\backups\...\admin\translations\private` (27 July precutover backup)
- `admin\translations\private` was not found as a current folder, only in that backup

Do not re-run `find_claude_scanners.ps1` against all of `C:\Alertness AI` (that walk hit 19,090 church-directory scripts).

## Where the other ~385 translations live

They are **not** missing from the catalog. They are missing from `C:\Alertness AI\website books` as language-tagged PDFs. The bookstore reader serves **EPUB** files from the Alertness Books server:

- Public site: https://alertnessbooks.com/ (same files as https://alertnessai.com/AlertnessBooks/)
- Protected dirs (Apache 403): `/data/` (ebook files), `/lib/` (`epub.js`, `lib_ui.php`), `/reader/` (sign-in at `/reader/library.php`)
- Public covers prove each language edition exists: `/assets/covers/thumb/{slug}_{lang}.jpg` (for example `econ-nie_es.jpg`, `btc-1_es.jpg`)
- Filenames on the server follow store slugs: `econ-nie_es.epub`, `btc-1_af.epub`, `vintage_bg_de.epub`
- `download.php` is the customer download link; it needs a purchase token, so do not scrape it. Copy the files from the server account instead.

On this Windows PC, first see whether the EPUBs and private HTML masters are already here (the checker used to ignore `.epub` and `.html`):

```powershell
cd $HOME\Osorno777.github.io\tools\translation_qa
.\find_local_translations.ps1
.\find_claude_scanners.ps1
```

`find_claude_scanners.ps1` looks in `C:\Alertness AI`, Writing, bookstore clones, and `agent_workflows` for Claude-written `.py` scanners and copies folder-path clues into `reports\claude_path_clues.tsv`. It also hunts `WORKORDERS_RELAY_*.md`, `LIC_EN_metadata.md`, `translate_html.py`, `fix_refusal_text.py`, and `admin\translations\private` into `reports\bookstore_clues.tsv`. Those scripts are not in this GitHub repo. Paste the TSVs back into chat (paths only).

If the EPUB/HTML list is still small, open cPanel Terminal / SSH on the bookstore host and run `find_server_ebooks.sh`, or in File Manager open the AlertnessBooks `data` folder (EPUBs) and `admin/translations/private` (HTML masters) and zip those files. Unpack EPUBs into `C:\Alertness AI\website books\store_epubs`. Unpack HTML into a local `admin\translations\private` folder. **Do not copy sidecar JSON.** Then `.\rescan.bat`.

The checker looks for English PDFs in the Writing folders *and* in `C:\Alertness AI\website books` (`01_*.pdf`, `*_EN_*_ebook_*.pdf`). Translations are walked from `C:\Alertness AI\website books`, from `C:\Alertness AI\bookstore\fulfillment\_out` (HTML rebuilds such as `btc-5_hi.html`), and from `admin/translations/private` when that folder exists (PDF, TXT, EPUB, and HTML). Pairing uses ISBNs, numbered stems (`01_` through `05_`), store slugs (`vintage_bg`, `econ-nie`, `btc-1`), catalog aliases (including accented Spanish titles), language folders (`Spanish`, `Amharic`, `es`), and filename tags (`_es`, `_ZH-HK`, `(French)`). It does not fuzzy-match shared words such as "primer", "chile", or "public policy" across different catalog books.

It skips Sims logs, `_freedom_data`, nohyph backups, audiobook silence logs, `DO-NOT-USE` / `BIODUP` files, sidecar JSON / sidecar `text` fields, and paperback KDP PDFs when an ebook PDF for the same book and language exists. A KDP PDF, a store EPUB, and a fulfillment HTML rebuild of the same language are **all scanned**; they can differ. It will not compare two English interiors of the same book, and it will not treat a sidecar `text` field as the lost original.

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
