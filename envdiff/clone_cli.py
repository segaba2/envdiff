"""CLI entry-point for the clone command."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.cloner import clone_to_file


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-clone",
        description="Clone a .env file to a new target with optional overrides and secret masking.",
    )
    p.add_argument("source", help="Source .env file")
    p.add_argument("target", help="Destination .env file to write")
    p.add_argument(
        "--set",
        metavar="KEY=VALUE",
        action="append",
        dest="overrides",
        default=[],
        help="Override a key in the clone (repeatable)",
    )
    p.add_argument(
        "--mask-secrets",
        action="store_true",
        default=False,
        help="Replace secret-looking values with a placeholder",
    )
    p.add_argument(
        "--mask-placeholder",
        default="CHANGE_ME",
        metavar="TEXT",
        help="Placeholder used when masking secrets (default: CHANGE_ME)",
    )
    return p


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    src = Path(args.source)
    if not src.is_file():
        print(f"error: source file not found: {src}", file=sys.stderr)
        return 1

    try:
        env = parse_env_file(src)
    except EnvParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    overrides: dict[str, str] = {}
    for item in args.overrides:
        if "=" not in item:
            print(f"error: --set value must be KEY=VALUE, got: {item!r}", file=sys.stderr)
            return 1
        k, _, v = item.partition("=")
        overrides[k.strip()] = v

    result = clone_to_file(
        env,
        source=str(src),
        target=Path(args.target),
        overrides=overrides,
        mask_secrets=args.mask_secrets,
        mask_placeholder=args.mask_placeholder,
    )

    print(result.summary())
    if result.overridden:
        print("overridden: " + ", ".join(result.overridden))
    if result.masked:
        print("masked:     " + ", ".join(result.masked))
    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
