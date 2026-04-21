"""CLI entry point for the transform sub-command."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.transformer import transform


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-transform",
        description="Apply key/value transformations to an .env file.",
    )
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--upper-keys",
        action="store_true",
        default=False,
        help="Uppercase all keys",
    )
    p.add_argument(
        "--strip-values",
        action="store_true",
        default=False,
        help="Strip surrounding whitespace from values",
    )
    p.add_argument(
        "--rename",
        metavar="OLD=NEW",
        action="append",
        default=[],
        help="Rename a key (repeatable)",
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

    rename_map: dict[str, str] = {}
    for pair in args.rename:
        if "=" not in pair:
            print(f"error: invalid --rename value '{pair}' (expected OLD=NEW)", file=sys.stderr)
            return 1
        old, new = pair.split("=", 1)
        rename_map[old] = new

    result = transform(
        env,
        upper_keys=args.upper_keys,
        strip_values=args.strip_values,
        rename=rename_map or None,
    )

    if args.format == "json":
        print(json.dumps({"transformed": result.transformed, "applied": result.applied}, indent=2))
    else:
        print(result.summary())
        for k, v in result.transformed.items():
            marker = "*" if k in result.applied else " "
            print(f"  [{marker}] {k}={v}")

    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
