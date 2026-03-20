"""
Tests for Feature: Token shape validation
"""
import json
import os
import subprocess
import sys

PYKEN = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pyken.py')
MAPPING = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mappings', 'python-to-javascript.yaml')


def run_pyken(*args, input_data=None):
    cmd = [sys.executable, PYKEN] + list(args)
    return subprocess.run(cmd, input=input_data, capture_output=True, text=True)


def test_token_missing_the_value_key_exits_with_a_clear_error():
    """Scenario: Token missing the value key exits with a clear error"""
    tokens = [{"type": "keyword"}]  # missing 'value' key
    result = run_pyken(MAPPING, input_data=json.dumps(tokens))
    assert result.returncode != 0
    assert "value" in result.stderr.lower() or "token" in result.stderr.lower() or "malformed" in result.stderr.lower()


def test_token_missing_the_type_key_exits_with_a_clear_error():
    """Scenario: Token missing the type key exits with a clear error"""
    tokens = [{"value": "def"}]  # missing 'type' key
    result = run_pyken(MAPPING, input_data=json.dumps(tokens))
    assert result.returncode != 0
    assert "type" in result.stderr.lower() or "token" in result.stderr.lower() or "malformed" in result.stderr.lower()


def test_token_that_is_not_a_json_object_exits_with_a_clear_error():
    """Scenario: Token that is not a JSON object exits with a clear error"""
    # String token
    result = run_pyken(MAPPING, input_data=json.dumps(["keyword"]))
    assert result.returncode != 0
    assert "object" in result.stderr.lower() or "token" in result.stderr.lower() or "malformed" in result.stderr.lower()
    
    # Number token
    result = run_pyken(MAPPING, input_data=json.dumps([123]))
    assert result.returncode != 0
    assert "object" in result.stderr.lower() or "token" in result.stderr.lower() or "malformed" in result.stderr.lower()
