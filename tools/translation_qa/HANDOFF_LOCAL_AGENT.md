# Handoff: Cloud Agent ? local Cursor on the Windows PC

You are the local Agent on John Cobin's Windows PC. This file is the brief. Open folder `C:\Users\dinam\Osorno777.github.io`. Use local Agent, not Cloud.

## Where the secrets are

Do not paste secret values into chat. Read the file if a command needs it.

1. **Checker (this repo)**  
   `C:\Users\dinam\Osorno777.github.io\tools\translation_qa\.env`  
   Created from `.env.example` by `setup.bat`. Gitignored.  
   Keys: `PDF_PASSWORDS` (semicolon-separated), `XAI_API_KEY`, `XAI_MODEL=grok-4.6`, optional Anthropic/OpenAI/DeepSeek/OpenRouter keys.

2. **Bookstore clone (separate tree, not this git repo)**  
   `C:\Alertness AI\bookstore\.env`  
   Also look for `.env` under `C:\Alertness AI\bookstore\qr_fix\` if a tool there asks for keys.

3. **Cursor Pro**  
   Desktop / `agent login` on this PC. Not stored in `.env`.

4. **Not secrets**  
   `paths.example.json` ? local `paths.json` (gitignored). Report output is `E:\translation_qa\reports`.

If `.env` is missing, tell John to copy `.env.example` to `.env` and fill it. Do not invent passwords.

## What is running

- One 1034-pair catalog scan via `.\rescan.bat`. Leave it. No second window. No `--llm`.
- Reports/temp on `E:\translation_qa`. Resume skips HTML already written.
- Checker only reports. Repair goes through the English master, never sidecar `text`.

## Live bookstore (paths only)

- `C:\Alertness AI\bookstore\public\store_catalog.json`
- `C:\Alertness AI\bookstore\WORKORDERS_RELAY_20260813_1330.md`
- HTML rebuilds: `fulfillment\_out\`, `qr_fix\_out\readers_work\`, `btw_rerender\`
- Skip: `stale_samples`, `_staging`, `_safety`, `*_bak`, INTERIOR, BIODUP, sidecar JSON

## Drive buy (if that is the task)

Under $100 USD does not buy a fast 4 TB SSD in Chile. From MercadoLibre: prefer ready-made `Kingston SXS1000 1TB` (~$200k CLP) or Kingston NV3 / Crucial E100 1 TB M.2 + NVMe USB-C case. Skip generic “4 tera SSD” listings.

## Startup files Cursor already loads

- Repo root `AGENTS.md` and `CLAUDE.md`
- `tools/translation_qa/AGENTS.md`
