# Alertness Books / Osorno777.github.io

This GitHub Pages repo is mostly the public site. The translation veracity checker lives under `tools/translation_qa/` and does **not** rewrite books, PDFs, or the bookstore.

## You are on the Windows PC

Open `C:\Users\dinam\Osorno777.github.io`. Use local Agent, not Cloud. Do not start a second catalog scan. Do not use `--llm` on the running catalog.

## Secrets (do not commit, do not paste into chat)

The checker loads `tools/translation_qa/.env` (gitignored). Template: `tools/translation_qa/.env.example`.

Expected keys (values stay in that file only):

- `PDF_PASSWORDS` — semicolon-separated bookstore PDF passwords
- `XAI_API_KEY` / `XAI_MODEL` — optional Grok judge (`--llm` only)
- optional: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY`, `OPENROUTER_API_KEY`

Cursor Pro is the desktop/CLI login, not a key in `.env`.

If `.env` is missing, look next to the checker, then in the bookstore tree. Never invent passwords. Never write secrets into `AGENTS.md`, git, or chat.

## Catalog scan

- One window: `tools\translation_qa\rescan.bat`
- Reports and temp: `E:\translation_qa\reports` and `E:\translation_qa\tmp`
- Resume = HTML already on `E:` is skipped
- Pairing is catalog IDs only. Do not fuzzy-match book titles.

## Do not

- Rewrite translation interiors from this repo
- Treat sidecar JSON `text` as the lost English original
- Walk all of `C:\Alertness AI` with `find_claude_scanners.ps1`
- Duplicate bookstore tools (`fix_refusal_text.py`, `lineage_detect.py`, `preflight_book_gate.py`, `verify_fix_landed.py`)

Details: `tools/translation_qa/AGENTS.md` and `tools/translation_qa/HANDOFF_LOCAL_AGENT.md`.
