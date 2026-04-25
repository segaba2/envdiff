"""CLI entry-point: envdiff-scope  — filter an .env file to a named scope."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.scoper import scope


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-scope",
        description="Filter an .env file to keys belonging to a named scope.",
    )
    p.add_argument("file", help="Path to the .env file")
    p.add_argument("scope", help="Scope name (used as prefix, e.g. 'app' → 'APP_')")
    p.add_argument(
        "--prefix",
        dest="prefixes",
        action="append",
        metavar="PREFIX",
        help="Explicit prefix(es) to match (repeatable). Overrides default.",
    )
    p.add_argument(
        "--strip-prefix",
        action="store_true",
        default=False,
        help="Remove the matched prefix from output key names.",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    p.add_argument(
        "--show-excluded",
        action="store_true",
        default=False,
        help="Also list excluded keys.",
    )
    return p


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    try:
        env = parse_env_file(path)
    except EnvParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = scope(
        env,
        args.scope,
        prefixes=args.prefixes,
        strip_prefix=args.strip_prefix,
    )

    if args.format == "json":
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(result.summary())
        print("\nMatched:")
        for k, v in sorted(result.matched.items()):
            print(f"  {k}={v}")
        if args.show_excluded:
            print("\nExcluded:")
            for k, v in sorted(result.excluded.items()):
                print(f"  {k}={v}")

    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())
