"""
Tests for Feature: Mapping configuration
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


def test_map_a_token_by_type_and_value():
    """Scenario: Map a token by type and value"""
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
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        out_tokens = json.loads(result.stdout)
        assert out_tokens[0]['value'] == 'function'
    finally:
        os.unlink(mapping_file)


def test_map_a_token_by_type_only():
    """Scenario: Map a token by type only"""
    mapping_yaml = """
rules:
  - match:
      type: whitespace
    emit:
      value: "_"
"""
    mapping_file = make_mapping_file(mapping_yaml)
    tokens = [
        {"type": "whitespace", "value": " "},
        {"type": "whitespace", "value": "\t"},
        {"type": "whitespace", "value": "\n"},
    ]
    try:
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        out_tokens = json.loads(result.stdout)
        assert all(t['value'] == '_' for t in out_tokens)
    finally:
        os.unlink(mapping_file)


def test_more_specific_rules_take_priority_over_general_rules():
    """Scenario: More specific rules take priority over general rules"""
    mapping_yaml = """
rules:
  - match:
      type: keyword
      value: "def"
    emit:
      value: "SPECIFIC"
  - match:
      type: keyword
    emit:
      value: "GENERAL"
"""
    mapping_file = make_mapping_file(mapping_yaml)
    tokens = [
        {"type": "keyword", "value": "def"},
        {"type": "keyword", "value": "if"},
    ]
    try:
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        out_tokens = json.loads(result.stdout)
        assert out_tokens[0]['value'] == 'SPECIFIC'
        assert out_tokens[1]['value'] == 'GENERAL'
    finally:
        os.unlink(mapping_file)
