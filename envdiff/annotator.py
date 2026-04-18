"""Annotate env keys with metadata tags."""
from __future__ import annotations
from typing import Dict, List, Set

SECRET_PATTERNS = ("KEY", "SECRET", "TOKEN", "PASS", "PASSWORD", "PRIVATE", "AUTH")


def _looks_secret(key: str) -> bool:
    upper = key.upper()
    return any(p in upper for p in SECRET_PATTERNS)


def annotate(env: Dict[str, str]) -> Dict[str, List[str]]:
    """Return a mapping of key -> list[tag] for every key in *env*."""
    annotations: Dict[str, List[str]] = {}
    for key, value in env.items():
        tags: List[str] = []
        if _looks_secret(key):
            tags.append("secret")
        if value == "":
            tags.append("blank")
        if value.startswith("http://") or value.startswith("https://"):
            tags.append("url")
        if value.isdigit():
            tags.append("numeric")
        annotations[key] = tags
    return annotations


def keys_by_tag(annotations: Dict[str, List[str]], tag: str) -> List[str]:
    """Return all keys that carry *tag*."""
    return [k for k, tags in annotations.items() if tag in tags]


def secret_keys(env: Dict[str, str]) -> List[str]:
    return keys_by_tag(annotate(env), "secret")


def blank_keys(env: Dict[str, str]) -> List[str]:
    return keys_by_tag(annotate(env), "blank")
