"""sanitize_cli.py – CLI wrapper for the sanitizer module."""
from __future__ import annotations

import argparse
import json
import sys

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.sanitizer import sanitize


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-sanitize",
        description="Strip unsafe characters from .env values.",
    )
    p.add_argument("file", help="Path to the .env file to sanitize.")
    p.add_argument(
        "--replacement",
        default="",
        metavar="STR",
        help="Replacement string for each unsafe character (default: remove).",
    )
    p.add_argument(
        "--no-strip-newlines",
        action="store_true",
        help="Do not collapse embedded newlines.",
    )
    p.add_argument(
        "--only",
        nargs="+",
        metavar="KEY",
        help="Restrict sanitization to these keys only.",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    return p


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        env = parse_env_file(args.file)
    except (EnvParseError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = sanitize(
        env,
        replacement=args.replacement,
        strip_newlines=not args.no_strip_newlines,
        only_keys=args.only,
    )

    if args.format == "json":
        print(json.dumps({
            "has_changes": result.has_changes(),
            "changed_keys": result.changed_keys,
            "sanitized": result.sanitized,
        }, indent=2))
    else:
        print(result.summary())
        for key in result.changed_keys:
            print(f"  {key}: {result.original[key]!r} -> {result.sanitized[key]!r}")

    return 1 if result.has_changes() else 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
