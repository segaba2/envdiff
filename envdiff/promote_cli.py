"""CLI entry-point for the promote command."""
from __future__ import annotations

import argparse
import json
import sys

from envdiff.parser import parse_env_file
from envdiff.promoter import promote


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-promote",
        description="Promote keys from a source .env file into a destination .env file.",
    )
    p.add_argument("source", help="Source .env file (keys are read from here).")
    p.add_argument("destination", help="Destination .env file (keys are promoted into here).")
    p.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        default=None,
        help="Specific keys to promote (default: all source keys).",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite conflicting keys in the destination.",
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
        src = parse_env_file(args.source)
        dst = parse_env_file(args.destination)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = promote(src, dst, keys=args.keys, overwrite=args.overwrite)

    if args.format == "json":
        out = {
            "promoted": result.promoted,
            "skipped": result.skipped,
            "conflicts": {
                k: {"source": v[0], "destination": v[1]}
                for k, v in result.conflicts.items()
            },
            "summary": result.summary(),
        }
        print(json.dumps(out, indent=2))
    else:
        print(result.summary())
        for key, (sv, dv) in result.conflicts.items():
            marker = "(overwritten)" if args.overwrite else "(skipped)"
            print(f"  CONFLICT {key}: src={sv!r} dst={dv!r} {marker}")

    return 1 if result.has_conflicts() and not args.overwrite else 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
