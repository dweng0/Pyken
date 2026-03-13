"""
Tests for Feature: Bundled mappings
"""
import json
import os
import subprocess
import sys

PYKEN = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pyken.py')
MAPPINGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mappings')
PY_TO_JS = os.path.join(MAPPINGS_DIR, 'python-to-javascript.yaml')
JS_TO_TS = os.path.join(MAPPINGS_DIR, 'javascript-to-typescript.yaml')
PY_TO_PSEUDO = os.path.join(MAPPINGS_DIR, 'python-to-pseudocode.yaml')


def run_pyken(*args, input_data=None):
    cmd = [sys.executable, PYKEN] + list(args)
    return subprocess.run(cmd, input=input_data, capture_output=True, text=True)


def test_python_to_javascript_mapping_remaps_def_to_function():
    """Scenario: Python-to-JavaScript mapping remaps def to function"""
    tokens = [
        {"type": "keyword", "value": "def"},
        {"type": "whitespace", "value": " "},
        {"type": "identifier", "value": "greet"},
    ]
    result = run_pyken(PY_TO_JS, input_data=json.dumps(tokens))
    assert result.returncode == 0
    assert "function" in result.stdout
    assert "def" not in result.stdout


def test_javascript_to_typescript_mapping_passes_through_valid_tokens():
    """Scenario: JavaScript-to-TypeScript mapping passes through valid tokens"""
    tokens = [
        {"type": "keyword", "value": "function"},
        {"type": "whitespace", "value": " "},
        {"type": "identifier", "value": "hello"},
        {"type": "punctuator", "value": "()"},
        {"type": "whitespace", "value": " "},
        {"type": "punctuator", "value": "{}"},
    ]
    result = run_pyken(JS_TO_TS, '--tokens', input_data=json.dumps(tokens))
    assert result.returncode == 0
    out_tokens = json.loads(result.stdout)
    assert len(out_tokens) == len(tokens)
    assert all('type' in t and 'value' in t for t in out_tokens)


def test_python_to_pseudocode_mapping_replaces_keywords_with_plain_english():
    """Scenario: Python-to-pseudocode mapping replaces keywords with plain English"""
    tokens = [
        {"type": "keyword", "value": "def"},
        {"type": "whitespace", "value": " "},
        {"type": "keyword", "value": "if"},
        {"type": "whitespace", "value": " "},
        {"type": "keyword", "value": "return"},
    ]
    result = run_pyken(PY_TO_PSEUDO, input_data=json.dumps(tokens))
    assert result.returncode == 0
    assert "FUNCTION" in result.stdout
    assert "IF" in result.stdout
    assert "RETURN" in result.stdout
    assert "def" not in result.stdout
