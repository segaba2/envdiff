"""CLI entry-point for the split command."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.splitter import split_to_files


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-split",
        description="Split a .env file into per-prefix files.",
    )
    p.add_argument("source", help="Source .env file to split")
    p.add_argument(
        "output_dir",
        help="Directory to write split files into",
    )
    p.add_argument(
        "--prefixes",
        nargs="+",
        metavar="PREFIX",
        default=None,
        help="Only extract these prefixes (others go to ungrouped)",
    )
    p.add_argument(
        "--min-group-size",
        type=int,
        default=1,
        metavar="N",
        help="Minimum keys required to form a group (default: 1)",
    )
    p.add_argument(
        "--no-ungrouped",
        action="store_true",
        help="Do not write ungrouped.env for keys without a prefix",
    )
    return p


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    source = Path(args.source)
    if not source.exists():
        print(f"error: file not found: {source}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir)

    try:
        result = split_to_files(
            source,
            output_dir,
            prefixes=args.prefixes,
            min_group_size=args.min_group_size,
            include_ungrouped=not args.no_ungrouped,
        )
    except Exception as exc:  # pragma: no cover
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(result.summary())
    for f in result.output_files:
        print(f"  wrote {f}")
    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
