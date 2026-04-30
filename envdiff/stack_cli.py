"""stack_cli.py – CLI entry-point for the stacker feature."""
from __future__ import annotations

import argparse
import sys

from envdiff.stacker import stack
from envdiff.stack_formatter import format_json, format_text


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-stack",
        description="Layer multiple .env files; later files override earlier ones.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help=".env files in stack order")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument("--no-color", action="store_true", help="Disable ANSI colours")
    return p


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    for f in args.files:
        try:
            open(f).close()
        except FileNotFoundError:
            print(f"error: file not found: {f}", file=sys.stderr)
            return 1

    result = stack(args.files)

    if args.format == "json":
        print(format_json(result))
    else:
        print(format_text(result, use_color=not args.no_color), end="")

    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
