from __future__ import annotations

import argparse
import sys
from pathlib import Path

from translation_qa.discover import (
    discover_pairs,
    infer_language,
    inventory_rows,
    load_config,
    select_english_sources,
    unmatched_translations,
)
from translation_qa.extract import ExtractionError
from translation_qa.passwords import load_dotenv, load_pdf_passwords
from translation_qa.pipeline import audit_files
from translation_qa.report import write_reports


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Slow word-by-word translation veracity checker for Alertness Books."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Compare one English source to one translation.")
    check.add_argument("--english", required=True, type=Path)
    check.add_argument("--translated", required=True, type=Path)
    check.add_argument("--lang", default="")
    _add_common(check)

    scan = sub.add_parser("scan", help="Scan a translations folder against configured English sources.")
    scan.add_argument("--config", required=True, type=Path)
    scan.add_argument("--book", default="", help="Optional book-id substring filter.")
    scan.add_argument("--lang-filter", default="", help="Optional language code filter, e.g. es,de,fr.")
    scan.add_argument("--force", action="store_true", help="Redo pairs that already have an HTML report.")
    _add_common(scan)

    listing = sub.add_parser("list", help="Show which English/translation pairs the config would check.")
    listing.add_argument("--config", required=True, type=Path)

    inventory = sub.add_parser("inventory", help="Dump every PDF found (English, paired, unmatched).")
    inventory.add_argument("--config", required=True, type=Path)

    args = parser.parse_args(argv)
    output_dir: Path = getattr(args, "output", Path("reports"))
    passwords = load_pdf_passwords()

    if args.command not in {"list", "inventory"} and not passwords:
        print(
            "No PDF_PASSWORDS set. Encrypted PDFs will fail. "
            "Copy .env.example to .env and add semicolon-separated passwords.",
            file=sys.stderr,
        )

    try:
        if args.command == "check":
            language = args.lang or infer_language(args.translated, passwords=passwords, peek=True)
            result = audit_files(
                args.english,
                args.translated,
                language,
                word_by_word=not args.fast,
                use_llm=args.llm,
                delay_seconds=args.delay,
                max_sentences=args.max_sentences,
                passwords=passwords,
            )
            stem = f"{args.english.stem}__{args.translated.stem}__{language}"
            paths = write_reports(result, output_dir, _safe(stem))
            _print_summary(result, paths)
            return _exit_code(result)

        config = load_config(args.config)
        output_dir = Path(config.get("output_dir") or output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if args.command == "inventory":
            return _print_inventory(config, output_dir, passwords)

        pairs = discover_pairs(config, passwords=passwords)
        if args.command == "list":
            return _print_list(config, pairs, output_dir, passwords)

        if args.book:
            needle = args.book.lower()
            pairs = [pair for pair in pairs if needle in pair.book_id or needle in pair.english.stem.lower()]
        if args.lang_filter:
            allowed = {item.strip().lower() for item in args.lang_filter.split(",") if item.strip()}
            pairs = [pair for pair in pairs if pair.language in allowed]
        if not pairs:
            print("No English/translation pairs found. Check paths in the config file.", file=sys.stderr)
            print("Run: py -m translation_qa inventory --config paths.json", file=sys.stderr)
            return 2

        print(f"Found {len(pairs)} pair(s) to check.")
        worst = 0
        skipped = 0
        failed = 0
        for index, pair in enumerate(pairs, start=1):
            language = pair.language
            if language == "und":
                language = infer_language(pair.translated, passwords=passwords, peek=True)
            stem = _safe(f"{pair.book_id}__{pair.translated.stem}__{language}")
            existing = output_dir / f"{stem}.html"
            if existing.exists() and not args.force:
                skipped += 1
                print(f"[{index}/{len(pairs)}] Resume skip {pair.book_id} -> {language}: {existing.name}")
                continue
            print(f"[{index}/{len(pairs)}] Checking {pair.book_id} -> {language} ({pair.translated.suffix.lower().lstrip('.') or 'file'}): {pair.translated}")
            try:
                result = audit_files(
                    pair.english,
                    pair.translated,
                    language,
                    word_by_word=not args.fast,
                    use_llm=args.llm,
                    delay_seconds=args.delay,
                    max_sentences=args.max_sentences,
                    passwords=passwords,
                )
            except ExtractionError as exc:
                failed += 1
                print(f"  skip unreadable: {exc}", file=sys.stderr)
                continue
            paths = write_reports(result, output_dir, stem)
            _print_summary(result, paths)
            worst = max(worst, _exit_code(result))
        if skipped:
            print(f"Resumed: skipped {skipped} pair(s) that already had reports. Use --force to redo.")
        if failed:
            print(f"Skipped {failed} unreadable file(s). The rest of the catalog still ran.")
        return worst
    except ExtractionError as exc:
        print(str(exc), file=sys.stderr)
        return 2


def _print_list(config: dict, pairs, output_dir: Path, passwords: list[str]) -> int:
    english_sources = select_english_sources(config)
    leftover = unmatched_translations(config, passwords=passwords)
    lines = [
        f"English books found: {len(english_sources)}",
    ]
    for path in sorted(english_sources, key=lambda item: item.name.lower()):
        lines.append(f"  EN {path}")
    lines.append(f"Translation pairs: {len(pairs)}")
    for pair in pairs:
        fmt = pair.translated.suffix.lower().lstrip(".") or "file"
        lines.append(f"  {pair.book_id} | {pair.language} | {fmt} | {pair.translated}")
    lines.append(f"Unmatched translation files: {len(leftover)}")
    for path, reason in leftover[:80]:
        lines.append(f"  skip ({reason}): {path}")
    if len(leftover) > 80:
        lines.append(f"  ... {len(leftover) - 80} more")
    if not english_sources:
        lines.append("No English PDFs found. Check english_dirs in paths.json.")
    elif not pairs:
        lines.append(
            "No translation pairs yet. Language can be in the filename, a language folder "
            "(_es, Spanish, es/), or detected from the PDF text. Run inventory and paste reports/list.txt."
        )
    text = "\n".join(lines) + "\n"
    print(text, end="")
    list_path = output_dir / "list.txt"
    list_path.write_text(text, encoding="utf-8")
    print(f"Wrote {list_path}")
    return 0


def _print_inventory(config: dict, output_dir: Path, passwords: list[str]) -> int:
    rows = inventory_rows(config, passwords=passwords)
    lines = ["role\tbook_id\tlanguage\tformat\tnote\tpath"]
    for row in rows:
        lines.append(
            "\t".join(
                [row["role"], row["book_id"], row["language"], row.get("format", ""), row["note"], row["path"]]
            )
        )
    text = "\n".join(lines) + "\n"
    print(text, end="")
    path = output_dir / "inventory.tsv"
    path.write_text(text, encoding="utf-8")
    print(f"Wrote {path}")
    print(
        f"Summary: {sum(1 for row in rows if row['role']=='english')} English, "
        f"{sum(1 for row in rows if row['role']=='translation')} paired, "
        f"{sum(1 for row in rows if row['role']=='unmatched')} unmatched, "
        f"{sum(1 for row in rows if row['role']=='translation' and row.get('format')=='epub')} epub pairs, "
        f"{sum(1 for row in rows if row['role']=='translation' and row.get('format')=='pdf')} pdf pairs"
    )
    return 0


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", type=Path, default=Path("reports"))
    parser.add_argument("--fast", action="store_true", help="Skip per-word coverage; keep refusal/number/structure checks.")
    parser.add_argument("--llm", action="store_true", help="Enable the slow LLM word-meaning judge.")
    parser.add_argument("--delay", type=float, default=0.0, help="Seconds to wait after each LLM sentence (slow mode).")
    parser.add_argument("--max-sentences", type=int, default=None, help="Limit aligned sentences (useful for a trial run).")


def _print_summary(result, paths: dict[str, Path]) -> None:
    counts = result.counts
    print(
        f"  {result.language}: {result.sentences_compared} sentences, "
        f"{result.words_checked} words, "
        f"{counts.get('critical', 0)} critical, "
        f"{counts.get('refusal', 0)} refusals, "
        f"{counts.get('defect', 0)} defects, "
        f"{counts.get('warning', 0)} warnings"
    )
    print(f"  report: {paths['html']}")


def _exit_code(result) -> int:
    counts = result.counts
    if counts.get("critical", 0) or counts.get("refusal", 0):
        return 1
    return 0


def _safe(stem: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in stem)[:180]
