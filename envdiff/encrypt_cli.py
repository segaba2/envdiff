"""CLI entry-point for encrypting / decrypting .env files."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.encryptor import encrypt, decrypt


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-encrypt",
        description="Encrypt or decrypt sensitive values in a .env file.",
    )
    p.add_argument("file", help="Path to the .env file")
    p.add_argument("--passphrase", required=True, help="Encryption passphrase")
    p.add_argument(
        "--mode",
        choices=["encrypt", "decrypt"],
        default="encrypt",
        help="Operation mode (default: encrypt)",
    )
    p.add_argument(
        "--keys",
        nargs="*",
        metavar="KEY",
        help="Explicit keys to encrypt (default: auto-detect secrets)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format",
    )
    return p


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    try:
        env = parse_env_file(path)
    except Exception as exc:  # noqa: BLE001
        print(f"Parse error: {exc}", file=sys.stderr)
        return 1

    if args.mode == "encrypt":
        result = encrypt(env, args.passphrase, keys=args.keys or None)
        output_env = result.env
        summary = result.summary()
    else:
        output_env = decrypt(env, args.passphrase)
        summary = f"Decrypted {sum(1 for v in output_env.values() if v)} key(s)."

    if args.fmt == "json":
        print(json.dumps({"summary": summary, "env": output_env}, indent=2))
    else:
        print(summary)
        for k, v in output_env.items():
            print(f"{k}={v}")

    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
