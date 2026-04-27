"""Tests for envdiff.digester."""
import json
from pathlib import Path

import pytest

from envdiff.digester import (
    DigestResult,
    compare_digests,
    digest_file,
    load_digest,
    save_digest,
)


@pytest.fixture
def env_file(tmp_path: Path):
    """Write a simple .env file and return its path."""
    f = tmp_path / ".env"
    f.write_text("API_KEY=secret\nDEBUG=true\n")
    return f


@pytest.fixture
def env_file_b(tmp_path: Path):
    f = tmp_path / ".env.b"
    f.write_text("API_KEY=other\nDEBUG=false\n")
    return f


def test_digest_returns_result(env_file):
    result = digest_file(env_file)
    assert isinstance(result, DigestResult)


def test_digest_sha256_is_hex(env_file):
    result = digest_file(env_file)
    assert len(result.sha256) == 64
    assert all(c in "0123456789abcdef" for c in result.sha256)


def test_digest_md5_is_hex(env_file):
    result = digest_file(env_file)
    assert len(result.md5) == 32


def test_digest_size_matches_file(env_file):
    result = digest_file(env_file)
    assert result.size == env_file.stat().st_size


def test_digest_path_stored(env_file):
    result = digest_file(env_file)
    assert result.path == str(env_file)


def test_compare_identical_files_match(env_file, tmp_path):
    copy = tmp_path / ".env.copy"
    copy.write_bytes(env_file.read_bytes())
    cmp = compare_digests(env_file, copy)
    assert cmp.match is True
    assert cmp.changed_algorithm is None


def test_compare_different_files_no_match(env_file, env_file_b):
    cmp = compare_digests(env_file, env_file_b)
    assert cmp.match is False
    assert cmp.changed_algorithm == "sha256"


def test_comparison_summary_identical(env_file, tmp_path):
    copy = tmp_path / ".env.copy"
    copy.write_bytes(env_file.read_bytes())
    cmp = compare_digests(env_file, copy)
    assert "identical" in cmp.summary()


def test_comparison_summary_differs(env_file, env_file_b):
    cmp = compare_digests(env_file, env_file_b)
    assert "differ" in cmp.summary()


def test_save_and_load_roundtrip(env_file, tmp_path):
    result = digest_file(env_file)
    out = tmp_path / "digest.json"
    save_digest(result, out)
    loaded = load_digest(out)
    assert loaded.sha256 == result.sha256
    assert loaded.md5 == result.md5
    assert loaded.size == result.size


def test_save_writes_valid_json(env_file, tmp_path):
    result = digest_file(env_file)
    out = tmp_path / "digest.json"
    save_digest(result, out)
    data = json.loads(out.read_text())
    assert "sha256" in data
    assert "md5" in data
    assert "size" in data


def test_to_dict_has_expected_keys(env_file):
    result = digest_file(env_file)
    d = result.to_dict()
    assert set(d.keys()) == {"path", "sha256", "md5", "size"}
