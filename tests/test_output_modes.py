"""
Tests for Feature: Output modes
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


def test_default_output_reconstructs_source_text():
    """Scenario: Default output reconstructs source text"""
    mapping_yaml = """
rules:
  - match:
      type: keyword
    emit: pass
  - match:
      type: whitespace
    emit: pass
  - match:
      type: identifier
    emit: pass
"""
    mapping_file = make_mapping_file(mapping_yaml)
    tokens = [
        {"type": "keyword", "value": "def"},
        {"type": "whitespace", "value": " "},
        {"type": "identifier", "value": "foo"},
    ]
    try:
        result = run_pyken(mapping_file, input_data=json.dumps(tokens))
        assert result.returncode == 0
        assert result.stdout == "def foo"
        # Should not be parseable as JSON array
        try:
            parsed = json.loads(result.stdout)
            assert not isinstance(parsed, list), "Output should not be a JSON array"
        except json.JSONDecodeError:
            pass  # Expected — it's plain text
    finally:
        os.unlink(mapping_file)


def test_tokens_flag_outputs_a_json_token_stream():
    """Scenario: --tokens flag outputs a JSON token stream"""
    mapping_yaml = """
rules:
  - match:
      type: keyword
    emit: pass
  - match:
      type: whitespace
    emit: pass
"""
    mapping_file = make_mapping_file(mapping_yaml)
    tokens = [
        {"type": "keyword", "value": "def"},
        {"type": "whitespace", "value": " "},
    ]
    try:
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        out_tokens = json.loads(result.stdout)
        assert isinstance(out_tokens, list)
        for tok in out_tokens:
            assert 'type' in tok
            assert 'value' in tok
    finally:
        os.unlink(mapping_file)
