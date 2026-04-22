"""Encrypt and decrypt sensitive values in a parsed env dict."""
from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.annotator import _looks_secret

_MARKER = "enc:"


def _derive_key(passphrase: str) -> bytes:
    """Derive a 32-byte key from a passphrase using SHA-256."""
    return hashlib.sha256(passphrase.encode()).digest()


def _xor_encrypt(value: str, key: bytes) -> str:
    """XOR-based symmetric encrypt; returns base64-encoded ciphertext."""
    data = value.encode()
    key_stream = (key[i % len(key)] for i in range(len(data)))
    encrypted = bytes(b ^ k for b, k in zip(data, key_stream))
    return base64.b64encode(encrypted).decode()


def _xor_decrypt(token: str, key: bytes) -> str:
    """Reverse of _xor_encrypt."""
    encrypted = base64.b64decode(token.encode())
    key_stream = (key[i % len(key)] for i in range(len(encrypted)))
    return bytes(b ^ k for b, k in zip(encrypted, key_stream)).decode()


@dataclass
class EncryptResult:
    env: Dict[str, str]
    encrypted_keys: List[str] = field(default_factory=list)

    def summary(self) -> str:
        if not self.encrypted_keys:
            return "No keys encrypted."
        keys = ", ".join(sorted(self.encrypted_keys))
        return f"Encrypted {len(self.encrypted_keys)} key(s): {keys}"


def encrypt(env: Dict[str, str], passphrase: str, keys: List[str] | None = None) -> EncryptResult:
    """Encrypt values for sensitive keys (or a specified list)."""
    key = _derive_key(passphrase)
    result: Dict[str, str] = {}
    encrypted_keys: List[str] = []

    for k, v in env.items():
        should_encrypt = (keys is not None and k in keys) or (
            keys is None and _looks_secret(k)
        )
        if should_encrypt and v and not v.startswith(_MARKER):
            result[k] = _MARKER + _xor_encrypt(v, key)
            encrypted_keys.append(k)
        else:
            result[k] = v

    return EncryptResult(env=result, encrypted_keys=encrypted_keys)


def decrypt(env: Dict[str, str], passphrase: str) -> Dict[str, str]:
    """Decrypt all values that carry the enc: marker."""
    key = _derive_key(passphrase)
    result: Dict[str, str] = {}
    for k, v in env.items():
        if v.startswith(_MARKER):
            result[k] = _xor_decrypt(v[len(_MARKER):], key)
        else:
            result[k] = v
    return result
