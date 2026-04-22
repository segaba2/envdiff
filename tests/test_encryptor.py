"""Tests for envdiff.encryptor and envdiff.encrypt_cli."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.encryptor import EncryptResult, decrypt, encrypt

PASS = "s3cr3t"


@pytest.fixture
def sample_env() -> dict:
    return {
        "DB_PASSWORD": "hunter2",
        "API_KEY": "abc123",
        "APP_NAME": "myapp",
        "DEBUG": "true",
    }


# --- encrypt ---

def test_encrypt_marks_secret_keys(sample_env):
    result = encrypt(sample_env, PASS)
    assert result.env["DB_PASSWORD"].startswith("enc:")
    assert result.env["API_KEY"].startswith("enc:")


def test_non_secret_keys_unchanged(sample_env):
    result = encrypt(sample_env, PASS)
    assert result.env["APP_NAME"] == "myapp"
    assert result.env["DEBUG"] == "true"


def test_encrypted_keys_list(sample_env):
    result = encrypt(sample_env, PASS)
    assert "DB_PASSWORD" in result.encrypted_keys
    assert "API_KEY" in result.encrypted_keys
    assert "APP_NAME" not in result.encrypted_keys


def test_explicit_keys_override_autodetect(sample_env):
    result = encrypt(sample_env, PASS, keys=["APP_NAME"])
    assert result.env["APP_NAME"].startswith("enc:")
    # auto-detected secrets NOT encrypted when explicit list given
    assert not result.env["DB_PASSWORD"].startswith("enc:")


def test_empty_value_not_encrypted(sample_env):
    sample_env["EMPTY_SECRET"] = ""
    result = encrypt(sample_env, PASS)
    assert result.env["EMPTY_SECRET"] == ""


def test_already_encrypted_not_double_encrypted(sample_env):
    first = encrypt(sample_env, PASS)
    second = encrypt(first.env, PASS)
    assert first.env["DB_PASSWORD"] == second.env["DB_PASSWORD"]


# --- decrypt ---

def test_roundtrip(sample_env):
    encrypted = encrypt(sample_env, PASS).env
    restored = decrypt(encrypted, PASS)
    assert restored["DB_PASSWORD"] == "hunter2"
    assert restored["API_KEY"] == "abc123"


def test_decrypt_leaves_plain_values_intact(sample_env):
    encrypted = encrypt(sample_env, PASS).env
    restored = decrypt(encrypted, PASS)
    assert restored["APP_NAME"] == "myapp"


# --- summary ---

def test_summary_no_keys():
    result = EncryptResult(env={}, encrypted_keys=[])
    assert result.summary() == "No keys encrypted."


def test_summary_with_keys():
    result = EncryptResult(env={}, encrypted_keys=["A", "B"])
    assert "2" in result.summary()
    assert "A" in result.summary()


# --- CLI ---

def test_cli_encrypt_text(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_PASSWORD=secret\nAPP_NAME=app\n")

    from envdiff.encrypt_cli import run
    rc = run([str(env_file), "--passphrase", PASS, "--mode", "encrypt"])
    assert rc == 0


def test_cli_missing_file(tmp_path: Path):
    from envdiff.encrypt_cli import run
    rc = run([str(tmp_path / "missing.env"), "--passphrase", PASS])
    assert rc == 1


def test_cli_json_output(tmp_path: Path, capsys):
    env_file = tmp_path / ".env"
    env_file.write_text("API_KEY=xyz\n")

    from envdiff.encrypt_cli import run
    run([str(env_file), "--passphrase", PASS, "--format", "json"])
    captured = capsys.readouterr().out
    data = json.loads(captured)
    assert "env" in data
    assert "summary" in data
