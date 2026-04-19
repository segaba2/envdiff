"""CLI entry point for batch multi-file diff."""
from __future__ import annotations
import argparse
import sys
from envdiff.differ_plus import diff_many
from envdiff.batch_reporter import render_text, render_json, exit_code


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-batch",
        description="Compare a base .env file against multiple others.",
    )
    p.add_argument("base", help="Base .env file")
    p.add_argument("others", nargs="+", help="Files to compare against base")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    return p


def run(args: argparse.Namespace) -> int:
    result = diff_many(args.base, args.others)
    if args.format == "json":
        print(render_json(result))
    else:
        print(render_text(result))
    return exit_code(result)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
