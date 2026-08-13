from __future__ import annotations

import argparse
import sys
from pathlib import Path

from translation_qa.discover import discover_pairs, infer_language, load_config
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
    _add_common(scan)

    args = parser.parse_args(argv)
    output_dir: Path = args.output
    passwords = load_pdf_passwords()
    if not passwords:
        print(
            "No PDF_PASSWORDS set. Encrypted PDFs will fail. "
            "Copy .env.example to .env and add semicolon-separated passwords.",
            file=sys.stderr,
        )

    try:
        if args.command == "check":
            language = args.lang or infer_language(args.translated)
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
        pairs = discover_pairs(config)
        if args.book:
            needle = args.book.lower()
            pairs = [pair for pair in pairs if needle in pair.book_id or needle in pair.english.stem.lower()]
        if args.lang_filter:
            allowed = {item.strip().lower() for item in args.lang_filter.split(",") if item.strip()}
            pairs = [pair for pair in pairs if pair.language in allowed]
        if not pairs:
            print("No English/translation pairs found. Check paths in the config file.", file=sys.stderr)
            return 2

        worst = 0
        for pair in pairs:
            print(f"Checking {pair.book_id} -> {pair.language}: {pair.translated}")
            result = audit_files(
                pair.english,
                pair.translated,
                pair.language,
                word_by_word=not args.fast,
                use_llm=args.llm,
                delay_seconds=args.delay,
                max_sentences=args.max_sentences,
                passwords=passwords,
            )
            stem = f"{pair.book_id}__{pair.translated.stem}__{pair.language}"
            paths = write_reports(result, output_dir, _safe(stem))
            _print_summary(result, paths)
            worst = max(worst, _exit_code(result))
        return worst
    except ExtractionError as exc:
        print(str(exc), file=sys.stderr)
        return 2


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
