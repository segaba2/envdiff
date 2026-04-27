"""CLI entry-point for the env migrator."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.migrator import migrate
from envdiff.parser import parse_env_file


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-migrate",
        description="Migrate keys in a .env file using a JSON rename map.",
    )
    p.add_argument("env_file", help="Source .env file")
    p.add_argument("--map", dest="rename_map", help="JSON file containing rename map")
    p.add_argument(
        "--drop",
        nargs="*",
        default=[],
        metavar="KEY",
        help="Keys to drop from output",
    )
    p.add_argument(
        "--no-keep-unmapped",
        action="store_false",
        dest="keep_unmapped",
        help="Omit keys not present in the rename map",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    p.add_argument("--out", help="Write migrated env to this file")
    return p


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    src = Path(args.env_file)
    if not src.exists():
        print(f"error: file not found: {src}", file=sys.stderr)
        return 1

    rename_map: dict[str, str] = {}
    if args.rename_map:
        map_path = Path(args.rename_map)
        if not map_path.exists():
            print(f"error: map file not found: {map_path}", file=sys.stderr)
            return 1
        rename_map = json.loads(map_path.read_text())

    env = parse_env_file(src)
    result = migrate(env, rename_map=rename_map, drop_keys=args.drop, keep_unmapped=args.keep_unmapped)

    if result.has_errors():
        for err in result.errors:
            print(f"error: {err}", file=sys.stderr)
        return 1

    if args.out:
        lines = [f"{k}={v}\n" for k, v in sorted(result.migrated.items())]
        Path(args.out).write_text("".join(lines))

    if args.format == "json":
        print(json.dumps({"migrated": result.migrated, "skipped": result.skipped, "dropped": result.dropped}, indent=2))
    else:
        print(f"Migration summary: {result.summary()}")
        for k, v in sorted(result.migrated.items()):
            print(f"  {k}={v}")
        if result.skipped:
            print("Skipped:", ", ".join(sorted(result.skipped)))
        if result.dropped:
            print("Dropped:", ", ".join(sorted(result.dropped)))

    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
