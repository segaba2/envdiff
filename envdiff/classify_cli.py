"""CLI entry-point: classify keys in a .env file by semantic category."""

from __future__ import annotations

import argparse
import json
import sys

from envdiff.classifier import classify
from envdiff.parser import parse_env_file, EnvParseError


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-classify",
        description="Classify .env keys into semantic categories.",
    )
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--category",
        metavar="CAT",
        help="Show only keys belonging to this category",
    )
    return p


def _format_text(result, category_filter: str | None) -> str:
    lines: list[str] = []
    by_cat = result.by_category

    if category_filter:
        cats = {category_filter: by_cat.get(category_filter, [])}
    else:
        cats = dict(sorted(by_cat.items()))

    for cat, keys in cats.items():
        lines.append(f"[{cat.upper()}]")
        for key in keys:
            lines.append(f"  {key}")

    return "\n".join(lines) if lines else "(no keys)"


def _format_json(result, category_filter: str | None) -> str:
    if category_filter:
        data = {category_filter: result.by_category.get(category_filter, [])}
    else:
        data = dict(sorted(result.by_category.items()))
    return json.dumps(data, indent=2)


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        env = parse_env_file(args.file)
    except (EnvParseError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = classify(env)

    if args.format == "json":
        print(_format_json(result, args.category))
    else:
        print(_format_text(result, args.category))
        print()
        print(result.summary())

    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
