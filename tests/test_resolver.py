"""Tests for envdiff.resolver."""
import pytest
from pathlib import Path

from envdiff.resolver import resolve


@pytest.fixture()
def env_dir(tmp_path: Path):
    base = tmp_path / ".env.base"
    base.write_text("APP=base\nDEBUG=false\nSECRET=base_secret\n")

    dev = tmp_path / ".env.dev"
    dev.write_text("DEBUG=true\nNEW_KEY=dev_value\n")

    prod = tmp_path / ".env.prod"
    prod.write_text("SECRET=prod_secret\nNEW_KEY=prod_value\n")

    return {"base": base, "dev": dev, "prod": prod}


def test_later_file_overrides_earlier(env_dir):
    result = resolve([env_dir["dev"]], base=env_dir["base"])
    assert result.effective["DEBUG"] == "true"


def test_base_values_kept_when_not_overridden(env_dir):
    result = resolve([env_dir["dev"]], base=env_dir["base"])
    assert result.effective["APP"] == "base"


def test_new_key_from_override_file(env_dir):
    result = resolve([env_dir["dev"]], base=env_dir["base"])
    assert result.effective["NEW_KEY"] == "dev_value"


def test_sources_track_winning_file(env_dir):
    result = resolve([env_dir["dev"]], base=env_dir["base"])
    assert result.sources["DEBUG"] == str(env_dir["dev"])
    assert result.sources["APP"] == str(env_dir["base"])


def test_overrides_records_all_definitions(env_dir):
    result = resolve([env_dir["dev"], env_dir["prod"]], base=env_dir["base"])
    assert len(result.overrides["NEW_KEY"]) == 2


def test_multiple_overrides_last_wins(env_dir):
    result = resolve([env_dir["dev"], env_dir["prod"]], base=env_dir["base"])
    assert result.effective["NEW_KEY"] == "prod_value"
    assert result.effective["SECRET"] == "prod_secret"


def test_no_base_file(env_dir):
    result = resolve([env_dir["dev"], env_dir["prod"]])
    assert "APP" not in result.effective
    assert result.effective["DEBUG"] == "true"


def test_summary_string(env_dir):
    result = resolve([env_dir["dev"], env_dir["prod"]], base=env_dir["base"])
    summary = result.summary()
    assert "resolved" in summary
    assert "overridden" in summary
