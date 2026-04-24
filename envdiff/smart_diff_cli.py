"""CLI entry-point for smart (type/case-aware) diff between two .env files."""
from __future__ import annotations
import argparse
import sys
from envdiff.parser import parse_env_file
from envdiff.comparator_plus import smart_compare
from envdiff.smart_diff_formatter import format_text, format_json


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-smart",
        description="Smart diff: flag case-only and type mismatches between two .env files.",
    )
    p.add_argument("file_a", help="First .env file (A)")
    p.add_argument("file_b", help="Second .env file (B)")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--color",
        action="store_true",
        default=False,
        help="Enable ANSI colour output (text format only)",
    )
    p.add_argument(
        "--only-diff",
        action="store_true",
        default=False,
        help="Exit 1 if any diff found, 0 otherwise (useful for CI)",
    )
    return p


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        env_a = parse_env_file(args.file_a)
        env_b = parse_env_file(args.file_b)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"Parse error: {exc}", file=sys.stderr)
        return 2

    result = smart_compare(env_a, env_b)

    if args.format == "json":
        print(format_json(result))
    else:
        print(format_text(result, use_color=args.color))

    if args.only_diff:
        return 1 if result.has_diff() else 0
    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
