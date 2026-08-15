# Translation veracity checker

Report-only Python tool. It does not rewrite PDFs, HTML, or EPUBs.

## Secrets

Read values from `.env` in this folder. Do not print them. Do not commit them.

| File | Role |
|---|---|
| `C:\Users\dinam\Osorno777.github.io\tools\translation_qa\.env` | Live secrets (gitignored) |
| `C:\Users\dinam\Osorno777.github.io\tools\translation_qa\.env.example` | Key names only |
| `C:\Alertness AI\bookstore\.env` | Bookstore clone, if present |

`setup.bat` copies `.env.example` ? `.env` if missing. `load_dotenv()` in `translation_qa/passwords.py` reads cwd `.env`, then this package folder.

## Scan

- `.\rescan.bat` — offload to `E:\translation_qa` first, then inventory, list, scan
- Output: `E:\translation_qa\reports`
- Resume skip: existing `*.html` reports
- Tests: `py -m pytest` from this folder

## Pairing

Catalog titles and store slugs only. Skip `stale_samples`, `_staging`, `_safety`, `*_bak`, INTERIOR, BIODUP, DO-NOT-USE, sidecar JSON, `und` language.
