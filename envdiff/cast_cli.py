"""CLI entry-point: show inferred types for keys in a .env file."""
from __future__ import annotations
import argparse
import json
import sys

from envdiff.parser import parse_env_file
from envdiff.caster import cast


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-cast",
        description="Infer and display value types for a .env file.",
    )
    p.add_argument("file", help="Path to .env file")
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

    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = cast(env)

    if args.format == "json":
        payload = {
            "file": args.file,
            "types": result.types,
            "values": {k: str(v) for k, v in result.values.items()},
        }
        print(json.dumps(payload, indent=2))
    else:
        print(f"File : {args.file}")
        print(result.summary())
        print()
        for key in sorted(result.types):
            print(f"  {key:<30} {result.types[key]:<8}  {result.values[key]!r}")

    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
