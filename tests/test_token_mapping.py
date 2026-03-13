"""
Tests for Feature: Apply token mapping
"""
import json
import os
import subprocess
import sys
import tempfile

PYKEN = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pyken.py')


def run_pyken(*args, input_data=None):
    cmd = [sys.executable, PYKEN] + list(args)
    return subprocess.run(cmd, input=input_data, capture_output=True, text=True)


def make_mapping_file(content):
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    f.write(content)
    f.close()
    return f.name


def test_mapped_token_value_is_replaced():
    """Scenario: Mapped token value is replaced"""
    mapping_yaml = """
rules:
  - match:
      type: keyword
      value: "def"
    emit:
      value: "function"
"""
    mapping_file = make_mapping_file(mapping_yaml)
    tokens = [{"type": "keyword", "value": "def"}]
    try:
        result = run_pyken(mapping_file, input_data=json.dumps(tokens))
        assert result.returncode == 0
        assert "function" in result.stdout
        assert "def" not in result.stdout
    finally:
        os.unlink(mapping_file)


def test_mapped_token_type_is_replaced():
    """Scenario: Mapped token type is replaced"""
    mapping_yaml = """
rules:
  - match:
      type: keyword
    emit:
      type: "reserved"
"""
    mapping_file = make_mapping_file(mapping_yaml)
    tokens = [{"type": "keyword", "value": "if"}]
    try:
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        out_tokens = json.loads(result.stdout)
        assert len(out_tokens) == 1
        assert out_tokens[0]['type'] == 'reserved'
    finally:
        os.unlink(mapping_file)


def test_unmapped_token_passes_through_unchanged_in_non_strict_mode():
    """Scenario: Unmapped token passes through unchanged in non-strict mode"""
    mapping_yaml = """
rules:
  - match:
      type: keyword
    emit: pass
"""
    mapping_file = make_mapping_file(mapping_yaml)
    tokens = [{"type": "unknown_type", "value": "mystery"}]
    try:
        result = run_pyken(mapping_file, input_data=json.dumps(tokens))
        assert result.returncode == 0
        assert "mystery" in result.stdout
        assert "Warning" in result.stderr or "warning" in result.stderr.lower()
    finally:
        os.unlink(mapping_file)


def test_unmapped_token_causes_failure_in_strict_mode():
    """Scenario: Unmapped token causes failure in strict mode"""
    mapping_yaml = """
rules:
  - match:
      type: keyword
    emit: pass
"""
    mapping_file = make_mapping_file(mapping_yaml)
    tokens = [{"type": "unknown_type", "value": "mystery"}]
    try:
        result = run_pyken(mapping_file, '--strict', input_data=json.dumps(tokens))
        assert result.returncode != 0
        assert "mystery" in result.stderr or "unknown_type" in result.stderr
    finally:
        os.unlink(mapping_file)
