"""trim_cli.py – CLI entry-point for the trim subcommand.

Usage examples
--------------
  envdiff-trim env.local --reference .env.template
  envdiff-trim env.local --reference .env.template --json
  envdiff-trim env.local --reference .env.template --in-place
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.trimmer import trim_to_template


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-trim",
        description="Remove stale keys from an env file using a reference template.",
    )
    p.add_argument("env", help="Path to the env file to trim.")
    p.add_argument(
        "--reference", required=True, metavar="FILE",
        help="Reference env / template file that defines active keys.",
    )
    p.add_argument(
        "--ignore-case", action="store_true",
        help="Compare key names case-insensitively.",
    )
    p.add_argument(
        "--json", dest="as_json", action="store_true",
        help="Output result as JSON.",
    )
    p.add_argument(
        "--in-place", action="store_true",
        help="Overwrite the env file with trimmed content (dry-run by default).",
    )
    return p


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    env_path = Path(args.env)
    ref_path = Path(args.reference)

    if not env_path.exists():
        print(f"error: env file not found: {env_path}", file=sys.stderr)
        return 2
    if not ref_path.exists():
        print(f"error: reference file not found: {ref_path}", file=sys.stderr)
        return 2

    env = parse_env_file(env_path)
    reference = parse_env_file(ref_path)

    result = trim_to_template(env, reference, ignore_case=args.ignore_case)

    if args.as_json:
        print(json.dumps({
            "kept": result.kept,
            "removed": result.removed,
            "has_removals": result.has_removals(),
        }, indent=2))
    else:
        print(result.summary())

    if args.in_place and result.has_removals():
        lines = [
            f"{k}={v}\n" for k, v in result.kept.items()
        ]
        env_path.write_text("".join(lines))
        print(f"Wrote trimmed file to {env_path}")

    return 1 if result.has_removals() else 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
