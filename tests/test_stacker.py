"""Tests for envdiff.stacker."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.stacker import StackEntry, StackResult, stack


@pytest.fixture()
def env_dir(tmp_path: Path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)

    return _write


def test_returns_stack_result(env_dir):
    f = env_dir("a.env", "KEY=val\n")
    result = stack([f])
    assert isinstance(result, StackResult)


def test_single_file_resolved(env_dir):
    f = env_dir("a.env", "FOO=bar\nBAZ=qux\n")
    result = stack([f])
    assert result.resolved == {"FOO": "bar", "BAZ": "qux"}


def test_later_file_overrides_earlier(env_dir):
    base = env_dir("base.env", "KEY=original\n")
    override = env_dir("override.env", "KEY=new\n")
    result = stack([base, override])
    assert result.resolved["KEY"] == "new"


def test_overridden_key_recorded(env_dir):
    base = env_dir("base.env", "KEY=original\n")
    override = env_dir("override.env", "KEY=new\n")
    result = stack([base, override])
    assert "KEY" in result.overridden_keys


def test_non_overridden_key_not_in_overridden(env_dir):
    base = env_dir("base.env", "KEY=val\nOTHER=x\n")
    override = env_dir("override.env", "KEY=new\n")
    result = stack([base, override])
    assert "OTHER" not in result.overridden_keys


def test_new_key_from_later_file(env_dir):
    base = env_dir("base.env", "A=1\n")
    extra = env_dir("extra.env", "B=2\n")
    result = stack([base, extra])
    assert "B" in result.resolved


def test_files_list_preserved(env_dir):
    f1 = env_dir("a.env", "X=1\n")
    f2 = env_dir("b.env", "Y=2\n")
    result = stack([f1, f2])
    assert result.files == [f1, f2]


def test_summary_string(env_dir):
    base = env_dir("base.env", "A=1\nB=2\n")
    over = env_dir("over.env", "A=99\n")
    result = stack([base, over])
    s = result.summary()
    assert "2 key(s)" in s
    assert "1 key(s) overridden" in s


def test_entries_sorted_alphabetically(env_dir):
    f = env_dir("a.env", "ZEBRA=z\nAPPLE=a\nMIDDLE=m\n")
    result = stack([f])
    keys = [e.key for e in result.entries]
    assert keys == sorted(keys)
