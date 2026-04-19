"""CLI for multi-file diff using differ_plus."""
from __future__ import annotations

import argparse
import sys

from envdiff.differ_plus import diff_many
from envdiff.batch_reporter import render_text, render_json, exit_code


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-multi",
        description="Compare multiple .env files against a base file.",
    )
    p.add_argument("base", help="Base .env file")
    p.add_argument("others", nargs="+", help="One or more .env files to compare")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--exclude",
        metavar="PATTERN",
        action="append",
        default=[],
        help="Exclude keys matching pattern (repeatable)",
    )
    p.add_argument(
        "--prefix",
        metavar="PREFIX",
        default=None,
        help="Only compare keys with this prefix",
    )
    return p


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    pairs = [(args.base, other) for other in args.others]
    result = diff_many(pairs, exclude=args.exclude, prefix=args.prefix)

    if args.format == "json":
        print(render_json(result))
    else:
        print(render_text(result))

    return exit_code(result)


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
