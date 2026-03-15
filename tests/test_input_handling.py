"""
Tests for Feature: Accept token stream input
"""
import json
import os
import subprocess
import sys
import tempfile

PYKEN = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pyken.py')
MAPPING = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mappings', 'python-to-javascript.yaml')


def run_pyken(*args, input_data=None):
    cmd = [sys.executable, PYKEN] + list(args)
    return subprocess.run(cmd, input=input_data, capture_output=True, text=True)


def test_read_json_token_stream_from_stdin():
    """Scenario: Read JSON token stream from stdin"""
    tokens = [{"type": "keyword", "value": "def"}, {"type": "whitespace", "value": " "}]
    result = run_pyken(MAPPING, input_data=json.dumps(tokens))
    assert result.returncode == 0
    assert "function" in result.stdout


def test_read_json_token_stream_from_a_file():
    """Scenario: Read JSON token stream from a file"""
    tokens = [{"type": "keyword", "value": "def"}, {"type": "whitespace", "value": " "}]
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(tokens, f)
        tmp_path = f.name
    try:
        result = run_pyken(MAPPING, '--input', tmp_path)
        assert result.returncode == 0
        assert "function" in result.stdout
    finally:
        os.unlink(tmp_path)


def test_invalid_json_input_exits_with_a_clear_error():
    """Scenario: Invalid JSON input exits with a clear error"""
    result = run_pyken(MAPPING, input_data="not valid json {{{")
    assert result.returncode != 0
    assert "JSON" in result.stderr or "json" in result.stderr.lower()


def test_token_stream_valid_json_but_not_array_exits_with_error():
    """Scenario: Token stream that is valid JSON but not an array exits with a clear error"""
    result = run_pyken(MAPPING, input_data='{"type": "keyword", "value": "def"}')
    assert result.returncode != 0
    assert "array" in result.stderr.lower()


def test_empty_token_stream_produces_empty_output():
    """Scenario: Empty token stream produces empty output"""
    result = run_pyken(MAPPING, input_data='[]')
    assert result.returncode == 0
    assert result.stdout == ''
