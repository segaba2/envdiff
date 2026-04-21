"""Tests for envdiff.caster."""
import pytest
from envdiff.caster import _infer_type, _cast, cast, CastResult


@pytest.fixture
def sample_env():
    return {
        "PORT": "8080",
        "DEBUG": "true",
        "RATIO": "3.14",
        "NAME": "myapp",
        "EMPTY": "",
        "ENABLED": "yes",
        "RETRIES": "5",
    }


def test_infer_int():
    assert _infer_type("42") == "int"


def test_infer_float():
    assert _infer_type("1.5") == "float"


def test_infer_bool_true():
    assert _infer_type("true") == "bool"
    assert _infer_type("yes") == "bool"
    assert _infer_type("1") == "bool"


def test_infer_bool_false():
    assert _infer_type("false") == "bool"
    assert _infer_type("no") == "bool"
    assert _infer_type("0") == "bool"


def test_infer_str():
    assert _infer_type("hello") == "str"


def test_infer_empty():
    assert _infer_type("") == "empty"


def test_cast_int():
    assert _cast("8080") == 8080
    assert isinstance(_cast("8080"), int)


def test_cast_float():
    result = _cast("3.14")
    assert abs(result - 3.14) < 1e-9
    assert isinstance(result, float)


def test_cast_bool_true():
    assert _cast("true") is True
    assert _cast("YES") is True


def test_cast_bool_false():
    assert _cast("false") is False
    assert _cast("0") is False


def test_cast_str():
    assert _cast("myapp") == "myapp"


def test_cast_empty():
    assert _cast("") == ""


def test_cast_full_env(sample_env):
    result = cast(sample_env)
    assert isinstance(result, CastResult)
    assert result.types["PORT"] == "int"
    assert result.values["PORT"] == 8080
    assert result.types["DEBUG"] == "bool"
    assert result.values["DEBUG"] is True
    assert result.types["RATIO"] == "float"
    assert result.types["NAME"] == "str"
    assert result.types["EMPTY"] == "empty"


def test_summary_string(sample_env):
    result = cast(sample_env)
    s = result.summary()
    assert "keys cast" in s
    assert "int=" in s or "bool=" in s


def test_all_keys_present(sample_env):
    result = cast(sample_env)
    assert set(result.types.keys()) == set(sample_env.keys())
    assert set(result.values.keys()) == set(sample_env.keys())
