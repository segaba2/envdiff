"""Tests for envdiff.comparator_plus."""
import pytest
from envdiff.comparator_plus import smart_compare, SmartDiffResult, _infer_type


# ---------------------------------------------------------------------------
# _infer_type
# ---------------------------------------------------------------------------

def test_infer_type_bool_true():
    assert _infer_type("true") == "bool"

def test_infer_type_bool_false():
    assert _infer_type("False") == "bool"

def test_infer_type_int():
    assert _infer_type("42") == "int"

def test_infer_type_float():
    assert _infer_type("3.14") == "float"

def test_infer_type_str():
    assert _infer_type("hello") == "str"

def test_infer_type_null():
    assert _infer_type(None) == "null"


# ---------------------------------------------------------------------------
# smart_compare — basic cases
# ---------------------------------------------------------------------------

def test_no_diff_identical():
    env = {"A": "1", "B": "hello"}
    result = smart_compare(env, env.copy())
    assert not result.has_diff()

def test_missing_in_b():
    result = smart_compare({"A": "1", "B": "2"}, {"A": "1"})
    assert result.has_diff()
    statuses = {e.key: e.status for e in result.entries}
    assert statuses["B"] == "missing_b"

def test_missing_in_a():
    result = smart_compare({"A": "1"}, {"A": "1", "B": "2"})
    statuses = {e.key: e.status for e in result.entries}
    assert statuses["B"] == "missing_a"

def test_mismatch_detected():
    result = smart_compare({"A": "foo"}, {"A": "bar"})
    entry = result.entries[0]
    assert entry.status == "mismatch"
    assert not entry.case_only


# ---------------------------------------------------------------------------
# case_only detection
# ---------------------------------------------------------------------------

def test_case_only_flag_set():
    result = smart_compare({"A": "Hello"}, {"A": "hello"})
    entry = result.entries[0]
    assert entry.status == "mismatch"
    assert entry.case_only is True

def test_case_only_keys_list():
    result = smart_compare({"A": "Yes", "B": "different"}, {"A": "yes", "B": "other"})
    assert "A" in result.case_only_keys()
    assert "B" not in result.case_only_keys()


# ---------------------------------------------------------------------------
# type_mismatch detection
# ---------------------------------------------------------------------------

def test_type_mismatch_str_vs_int():
    result = smart_compare({"PORT": "abc"}, {"PORT": "8080"})
    entry = next(e for e in result.entries if e.key == "PORT")
    assert entry.type_mismatch is True

def test_no_type_mismatch_same_type():
    result = smart_compare({"PORT": "8080"}, {"PORT": "9090"})
    entry = result.entries[0]
    assert entry.type_mismatch is False

def test_type_mismatch_keys_list():
    result = smart_compare({"A": "true", "B": "hello"}, {"A": "1", "B": "world"})
    assert "A" in result.type_mismatch_keys()
    assert "B" not in result.type_mismatch_keys()


# ---------------------------------------------------------------------------
# summary & to_dict
# ---------------------------------------------------------------------------

def test_summary_string():
    result = smart_compare({"A": "1", "B": "x"}, {"A": "2"})
    s = result.summary()
    assert "mismatches=" in s
    assert "missing_b=" in s

def test_entry_to_dict_keys():
    result = smart_compare({"A": "1"}, {"A": "2"})
    d = result.entries[0].to_dict()
    assert set(d.keys()) == {"key", "value_a", "value_b", "status", "case_only", "type_mismatch"}
