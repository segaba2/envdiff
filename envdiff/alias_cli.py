"""alias_cli.py – CLI interface for the aliaser module.

Usage examples::

    envdiff-alias .env --map OLD_API_KEY=API_KEY
    envdiff-alias .env --map OLD_HOST=DB_HOST --map OLD_PORT=DB_PORT --format json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.aliaser import alias
from envdiff.parser import parse_env_file, EnvParseError


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-alias",
        description="Resolve alias keys to canonical names in a .env file.",
    )
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--map",
        metavar="ALIAS=CANONICAL",
        action="append",
        default=[],
        dest="mappings",
        help="Alias mapping in the form ALIAS_KEY=CANONICAL_KEY (repeatable)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    return p


def _parse_mappings(raw: list[str]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for item in raw:
        if "=" not in item:
            raise ValueError(f"Invalid mapping (expected ALIAS=CANONICAL): {item!r}")
        alias_key, canonical = item.split("=", 1)
        aliases[alias_key.strip()] = canonical.strip()
    return aliases


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

    try:
        aliases = _parse_mappings(args.mappings)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = alias(env, aliases)

    if args.format == "json":
        print(json.dumps({
            "env": result.env,
            "applied": result.applied,
            "missing": result.missing,
            "conflicts": result.conflicts,
            "summary": result.summary(),
        }, indent=2))
    else:
        print(f"Summary : {result.summary()}")
        if result.applied:
            print("Applied :")
            for a, c in sorted(result.applied.items()):
                print(f"  {a} -> {c}")
        if result.missing:
            print("Missing :")
            for k in result.missing:
                print(f"  {k}")
        if result.conflicts:
            print("Conflicts:")
            for canonical, aliased in sorted(result.conflicts.items()):
                print(f"  {canonical} <-> {', '.join(aliased)}")

    return 1 if result.has_conflicts() else 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
