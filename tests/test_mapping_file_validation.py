"""
Tests for Feature: Mapping file validation and Emit mode validation
"""
import json
import os
import subprocess
import sys
import tempfile
import yaml

PYKEN = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pyken.py')


def run_pyken_with_mapping(mapping_content, input_tokens=None):
    """Run pyken.py with a dynamically created mapping file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(yaml.safe_load(mapping_content), f)
        mapping_file = f.name
    
    try:
        if input_tokens is None:
            input_tokens = [{"type": "keyword", "value": "def"}]
        
        # Use JSON for token stream
        if isinstance(input_tokens, list):
            input_data = json.dumps(input_tokens)
        else:
            input_data = input_tokens
        
        # Use stdin for input
        cmd = [sys.executable, PYKEN, mapping_file]
        result = subprocess.run(cmd, input=input_data, capture_output=True, text=True)
        return result
    finally:
        os.unlink(mapping_file)


def test_rule_with_an_unknown_emit_mode_exits_with_a_clear_error():
    """Scenario: Rule with an unknown emit mode exits with a clear error"""
    mapping = """
rules:
  - match:
      type: keyword
      value: def
    emit: unknown_emit_mode
"""
    result = run_pyken_with_mapping(mapping)
    assert result.returncode != 0, "Expected non-zero exit code for unknown emit mode"
    assert "unknown" in result.stderr.lower() or "emit" in result.stderr.lower(), \
        f"Expected error message mentioning unknown emit mode, got: {result.stderr}"


def test_rule_missing_a_match_block_is_skipped_with_a_warning():
    """Scenario: Rule missing a match block is skipped with a warning"""
    mapping = """
rules:
  - emit: pass
"""
    result = run_pyken_with_mapping(mapping)
    # Should continue processing (exit code 0) and emit a warning
    assert result.returncode == 0, "Expected exit code 0 when rule with no match block is skipped"
    assert "warning" in result.stderr.lower() or "skip" in result.stderr.lower(), \
        f"Expected warning about skipped rule, got: {result.stderr}"


def test_unknown_emit_string_is_rejected_with_a_clear_error():
    """Scenario: Unknown emit string is rejected with a clear error"""
    mapping = """
rules:
  - match:
      type: keyword
    emit: dicard  # typo for 'discard'
"""
    result = run_pyken_with_mapping(mapping)
    assert result.returncode != 0, "Expected non-zero exit code for unknown emit string"
    assert "unknown" in result.stderr.lower() or "emit" in result.stderr.lower(), \
        f"Expected error message about unknown emit, got: {result.stderr}"


def test_valid_emit_string_values_are_accepted():
    """Scenario: Valid emit string values are accepted"""
    mapping = """
rules:
  - match:
      type: keyword
      value: def
    emit: pass
  - match:
      type: keyword
      value: return
    emit: discard
"""
    tokens = [
        {"type": "keyword", "value": "def"},
        {"type": "keyword", "value": "return"},
        {"type": "keyword", "value": "if"}
    ]
    result = run_pyken_with_mapping(mapping, tokens)
    assert result.returncode == 0, f"Expected exit code 0 for valid emit values, got: {result.stderr}"


def test_emit_as_a_dict_with_unrecognised_keys_is_rejected():
    """Scenario: Emit as a dict with unrecognised keys is rejected"""
    mapping = """
rules:
  - match:
      type: keyword
      value: def
    emit:
      frobnicate: something
"""
    result = run_pyken_with_mapping(mapping)
    assert result.returncode != 0, "Expected non-zero exit code for unknown emit key"
    assert "unknown" in result.stderr.lower() or "frobnicate" in result.stderr.lower(), \
        f"Expected error message about unknown emit key, got: {result.stderr}"
