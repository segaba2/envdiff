"""CLI entry-point for the flatten / unflatten feature.

Usage examples::

    envdiff-flatten env.env
    envdiff-flatten env.env --delimiter . --max-depth 2
    envdiff-flatten env.env --unflatten --format json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.flattener import flatten, unflatten


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-flatten",
        description="Flatten compound env keys (e.g. DB__HOST) into dot notation.",
    )
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--delimiter",
        default="__",
        metavar="SEP",
        help="Key segment separator (default: '__')",
    )
    p.add_argument(
        "--max-depth",
        type=int,
        default=None,
        metavar="N",
        help="Maximum nesting depth to expand",
    )
    p.add_argument(
        "--unflatten",
        action="store_true",
        help="Reverse mode: convert dot keys back to delimiter-separated uppercase keys",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    return p


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    env = parse_env_file(path)

    if args.unflatten:
        result_dict = unflatten(env, delimiter=args.delimiter)
        if args.format == "json":
            print(json.dumps(result_dict, indent=2))
        else:
            for k, v in sorted(result_dict.items()):
                print(f"{k}={v}")
        return 0

    result = flatten(env, delimiter=args.delimiter, max_depth=args.max_depth)

    if args.format == "json":
        payload = {
            "flat": result.flat,
            "mapping": result.mapping,
            "skipped": result.skipped,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(result.summary())
        print()
        for flat_key, value in sorted(result.flat.items()):
            original = result.mapping[flat_key]
            print(f"{flat_key}={value}  (was: {original})")
        if result.skipped:
            print("\nSkipped (collision or empty):")
            for k in result.skipped:
                print(f"  {k}")

    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
