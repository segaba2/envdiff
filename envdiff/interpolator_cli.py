"""CLI for interpolating variable references within a .env file."""

import argparse
import json
import sys

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.interpolator import interpolate


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-interpolate",
        description="Expand $VAR references inside a .env file.",
    )
    p.add_argument("file", help="Path to the .env file")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any references remain unresolved",
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

    result = interpolate(env)

    if args.format == "json":
        print(json.dumps({
            "resolved": result.resolved,
            "unresolved": result.unresolved,
            "env": result.env,
        }, indent=2))
    else:
        for key, value in result.env.items():
            marker = " [UNRESOLVED]" if key in result.unresolved else ""
            print(f"{key}={value}{marker}")
        if result.unresolved:
            print(f"\n{len(result.unresolved)} unresolved reference(s): {', '.join(sorted(result.unresolved))}",
                  file=sys.stderr)

    if args.strict and result.has_unresolved:
        return 1
    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
